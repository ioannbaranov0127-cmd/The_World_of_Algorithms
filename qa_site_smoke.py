# -*- coding: utf-8 -*-
"""Расширенный smoke-тест сайта: страницы, auth, admin, API, регрессии."""
from __future__ import annotations

import json
import os
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parent

# Локальный QA не должен падать из-за Render-guard
os.environ.setdefault('FLASK_DEBUG', '1')

from app import app  # noqa: E402
from course_data.loader import TASK_BY_ID  # noqa: E402

PWD = 'qa-smoke-pass-9'
NAME = 'QA Smoke'


def _uid() -> str:
    return uuid.uuid4().hex[:8]


def issue(report: dict, msg: str) -> None:
    report['issues'].append(msg)


def main() -> int:
    report: dict = {
        'issues': [],
        'checks': {},
    }
    suffix = _uid()
    student_email = f'student-{suffix}@test.local'
    admin_email = os.environ.get('ADMIN_EMAIL', f'admin-{suffix}@test.local').strip().lower()

    app.config['ADMIN_EMAIL'] = admin_email

    guest = app.test_client()

    for path in ('/', '/login', '/register', '/calorie-calculator', '/health'):
        r = guest.get(path)
        report['checks'][f'guest {path}'] = r.status_code
        if r.status_code != 200:
            issue(report, f'guest {path}: expected 200, got {r.status_code}')

    for path in ('/learn', '/profile', '/admin', '/api/session'):
        r = guest.get(path)
        report['checks'][f'guest {path}'] = r.status_code
        if r.status_code not in (302, 401):
            issue(report, f'guest {path}: expected redirect/401, got {r.status_code}')

    # --- student flow ---
    st = app.test_client()
    reg = st.post(
        '/register',
        data={
            'name': NAME,
            'email': student_email,
            'password': PWD,
            'password2': PWD,
        },
        follow_redirects=False,
    )
    if reg.status_code not in (302, 303):
        issue(report, f'student register: {reg.status_code}')

    for path in ('/learn', '/profile'):
        r = st.get(path, follow_redirects=True)
        report['checks'][f'student {path}'] = r.status_code
        if r.status_code != 200:
            issue(report, f'student {path}: {r.status_code}')
        if path == '/learn' and b'learn-config' not in r.data:
            issue(report, 'learn page missing learn-config')
        if path == '/learn' and b'userId' not in r.data:
            issue(report, 'learn-config missing userId')

    sess = st.get('/api/session')
    if sess.status_code != 200:
        issue(report, f'/api/session: {sess.status_code}')
    else:
        payload = sess.get_json() or {}
        if 'course_grade' not in payload:
            issue(report, '/api/session missing course_grade')
        if 'total_xp' in payload or 'level' in payload:
            issue(report, '/api/session still exposes XP/level')
        if 'xp_gained' in payload:
            issue(report, '/api/session exposes xp_gained')

    task6 = TASK_BY_ID[6]
    chk = st.post('/check_task', json={'task_id': 6, 'answer': task6['correct_order']})
    if chk.status_code != 200:
        issue(report, f'check_task #6 http {chk.status_code}')
    else:
        data = chk.get_json() or {}
        if data.get('success') is not True and data.get('already_completed') is not True:
            issue(report, 'check_task #6 failed with empty ordering')

    st_denied = st.get('/admin', follow_redirects=True)
    if st_denied.status_code != 403:
        issue(report, f'student /admin expected 403, got {st_denied.status_code}')

    # --- admin flow ---
    adm = app.test_client()
    areg = adm.post(
        '/register',
        data={
            'name': 'Admin QA',
            'email': admin_email,
            'password': PWD,
            'password2': PWD,
        },
        follow_redirects=True,
    )
    if areg.status_code != 200:
        issue(report, f'admin register: {areg.status_code}')

    from models import User

    with app.app_context():
        u = User.query.filter_by(email=admin_email).first()
        if u is None or not u.is_admin:
            issue(report, 'admin user not created with admin role')

    aidx = adm.get('/admin', follow_redirects=True)
    if aidx.status_code != 200:
        issue(report, f'admin index: {aidx.status_code}')
    if b'account-logout-form' not in aidx.data:
        issue(report, 'admin index missing logout button')

    prof = adm.get('/profile', follow_redirects=False)
    if prof.status_code not in (302, 303):
        issue(report, f'admin /profile should redirect, got {prof.status_code}')

    csv = adm.get('/admin/export.csv')
    if csv.status_code != 200:
        issue(report, f'admin csv: {csv.status_code}')

    # --- logout ---
    out = adm.post('/logout', follow_redirects=False)
    if out.status_code not in (302, 303):
        issue(report, f'logout: {out.status_code}')

    report['all_ok'] = not report['issues']
    out_path = ROOT / 'qa_site_smoke_report.json'
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print('Site smoke checks:', len(report['checks']), 'issues:', len(report['issues']))
    for msg in report['issues']:
        print(' -', msg)
    return 0 if report['all_ok'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
