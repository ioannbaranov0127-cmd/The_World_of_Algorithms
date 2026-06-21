# -*- coding: utf-8 -*-
"""HTTP smoke: check_code для всех project_stage через Flask test client."""
import json
from pathlib import Path

from app import app
from course_data.loader import TASK_BY_ID
from qa_project_stages import M1_REFERENCE, M1_STDIN

ROOT = Path(__file__).resolve().parent

M1_CHAIN = [6, 100, 101, 102, 103, 104, 105, 106, 107, 108]
M2_CHAIN = [310, 329, 340, 360, 373, 399, 419, 439, 459, 485]

QA_EMAIL = 'qa-http@test.local'
QA_PASSWORD = 'qa-test-pass-123'
QA_NAME = 'QA HTTP'
QA_ADMIN_EMAIL = 'qa-admin@test.local'
QA_ADMIN_PASSWORD = 'qa-admin-pass-123'


def m2_ref_code(tid: int) -> str:
    import _test_m2_ref as ref  # noqa: WPS433
    return ref.M2_REF[tid]


def ensure_logged_in(client) -> None:
    client.post(
        '/register',
        data={
            'name': QA_NAME,
            'email': QA_EMAIL,
            'password': QA_PASSWORD,
            'password2': QA_PASSWORD,
        },
        follow_redirects=False,
    )
    resp = client.post(
        '/login',
        data={'email': QA_EMAIL, 'password': QA_PASSWORD, 'next': '/learn'},
        follow_redirects=True,
    )
    if resp.status_code not in (200, 302):
        raise RuntimeError(f'QA login failed: {resp.status_code}')


def ensure_admin_user() -> None:
    from db import db
    from models import User
    from progress_service import ensure_progress_row

    with app.app_context():
        user = User.query.filter_by(email=QA_ADMIN_EMAIL).first()
        if user is None:
            user = User(email=QA_ADMIN_EMAIL, name='QA Admin', role='admin')
            user.set_password(QA_ADMIN_PASSWORD)
            db.session.add(user)
            db.session.commit()
        elif user.role != 'admin':
            user.role = 'admin'
            db.session.commit()
        ensure_progress_row(user.id)


def check_admin_smoke(report: dict) -> None:
    ensure_admin_user()
    student = app.test_client()
    ensure_logged_in(student)

    denied = student.get('/admin', follow_redirects=True)
    report.setdefault('admin', {})['student_forbidden'] = denied.status_code
    if denied.status_code != 403:
        report['issues'].append(f'admin: student expected 403, got {denied.status_code}')

    admin = app.test_client()
    login = admin.post(
        '/login',
        data={'email': QA_ADMIN_EMAIL, 'password': QA_ADMIN_PASSWORD},
        follow_redirects=True,
    )
    if login.status_code not in (200, 302):
        report['issues'].append(f'admin: login failed {login.status_code}')
        return

    index = admin.get('/admin', follow_redirects=True)
    report['admin']['index'] = index.status_code
    if index.status_code != 200:
        report['issues'].append(f'admin: index expected 200, got {index.status_code}')

    export = admin.get('/admin/export.csv')
    report['admin']['export'] = export.status_code
    if export.status_code != 200 or 'text/csv' not in (export.content_type or ''):
        report['issues'].append('admin: CSV export failed')

    from models import User

    with app.app_context():
        student_user = User.query.filter_by(email=QA_EMAIL).first()
        student_id = student_user.id if student_user else None

    if student_id is None:
        report['issues'].append('admin: QA student not found for detail/reset')
        return

    detail = admin.get(f'/admin/students/{student_id}', follow_redirects=True)
    report['admin']['student_detail'] = detail.status_code
    if detail.status_code != 200:
        report['issues'].append(f'admin: student detail expected 200, got {detail.status_code}')

    reset = admin.post(f'/admin/students/{student_id}/reset', follow_redirects=True)
    report['admin']['student_reset'] = reset.status_code
    if reset.status_code != 200:
        report['issues'].append(f'admin: reset expected 200, got {reset.status_code}')

    disposable = app.test_client()
    disposable.post(
        '/register',
        data={
            'name': 'DelMe',
            'email': 'del-me@test.local',
            'password': QA_PASSWORD,
            'password2': QA_PASSWORD,
        },
        follow_redirects=False,
    )
    with app.app_context():
        from models import User
        del_user = User.query.filter_by(email='del-me@test.local').first()
        del_id = del_user.id if del_user else None
    if del_id:
        deleted = admin.post(f'/admin/students/{del_id}/delete', follow_redirects=True)
        report['admin']['student_delete'] = deleted.status_code
        if deleted.status_code != 200:
            report['issues'].append(f'admin: delete expected 200, got {deleted.status_code}')
        with app.app_context():
            gone = User.query.filter_by(id=del_id).first() is None
        if not gone:
            report['issues'].append('admin: user still in DB after delete')


def main() -> int:
    report = {'checks': [], 'issues': []}
    client = app.test_client()

    r = client.get('/health')
    report['health'] = r.status_code

    ensure_logged_in(client)
    client.post('/reset_progress', json={})

    task6 = TASK_BY_ID[6]
    resp = client.post('/check_task', json={
        'task_id': 6,
        'answer': task6['correct_order'],
    })
    data = resp.get_json() or {}
    report['checks'].append({'id': 6, 'type': 'ordering', 'success': data.get('success')})
    if not data.get('success'):
        report['issues'].append('#6 ordering failed')

    for tid in M1_CHAIN[1:]:
        code = M1_REFERENCE[tid]
        stdin = M1_STDIN.get(tid, '')
        resp = client.post('/check_code', json={'task_id': tid, 'code': code, 'stdin': stdin})
        data = resp.get_json() or {}
        ok = resp.status_code == 200 and data.get('success') is True
        entry = {'id': tid, 'module': 1, 'http': resp.status_code, 'success': data.get('success')}
        if not ok:
            entry['error'] = data.get('error') or data.get('test_failures')
            report['issues'].append(f'#{tid} M1: {entry.get("error")}')
        report['checks'].append(entry)

    for tid in M2_CHAIN:
        code = m2_ref_code(tid)
        resp = client.post('/check_code', json={'task_id': tid, 'code': code, 'stdin': ''})
        data = resp.get_json() or {}
        ok = resp.status_code == 200 and data.get('success') is True
        entry = {
            'id': tid,
            'module': 2,
            'http': resp.status_code,
            'success': data.get('success'),
            'stdin_for_check': (data.get('stdin_for_check') or '')[:40],
        }
        if not ok:
            entry['error'] = data.get('error') or data.get('test_failures')
            report['issues'].append(f'#{tid} M2: {entry.get("error")}')
        report['checks'].append(entry)

    for path in ('/', '/learn', '/calorie-calculator', '/profile'):
        pr = client.get(path)
        report.setdefault('pages', {})[path] = pr.status_code

    check_admin_smoke(report)

    report['all_ok'] = len(report['issues']) == 0
    out = ROOT / 'qa_http_report.json'
    with open(out, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print('HTTP chain checks:', len(report['checks']), 'issues:', len(report['issues']))
    for issue in report['issues']:
        print(' -', issue)
    return 1 if report['issues'] else 0


if __name__ == '__main__':
    raise SystemExit(main())
