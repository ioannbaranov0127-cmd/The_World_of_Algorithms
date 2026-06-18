(function (global) {
    function showNotification(message, type) {
        var el = document.getElementById('toast-notification');
        if (!el) {
            el = document.createElement('div');
            el.id = 'toast-notification';
            el.className = 'toast-notification';
            document.body.appendChild(el);
        }
        var colors = { success: 'var(--toast-ok)', error: 'var(--toast-err)', info: 'var(--toast-info)' };
        el.style.background = colors[type] || colors.info;
        el.textContent = message;
        el.style.display = 'block';
        el.setAttribute('data-show', '1');
        clearTimeout(global._toastTimer);
        global._toastTimer = setTimeout(function () {
            el.removeAttribute('data-show');
            el.style.display = 'none';
        }, 3800);
    }
    global.showNotification = showNotification;

    var COURSE_GRADE_DEMO_KEY = 'learn-course-grade-demo-step-count';

    function readCourseGradeDemoConfig() {
        var el = document.getElementById('course-grade-demo-config');
        if (!el) return null;
        try {
            return JSON.parse(el.textContent || '{}');
        } catch (e) {
            return null;
        }
    }

    function readCourseGradeDemoStepCount(config) {
        try {
            var raw = localStorage.getItem(COURSE_GRADE_DEMO_KEY);
            if (raw === null || raw === '') return null;
            var steps = (config && config.steps) || [];
            var value = Math.round(Number(raw) || 0);
            return Math.max(0, Math.min(steps.length, value));
        } catch (e) {
            return null;
        }
    }

    function courseGradeLabel(percent) {
        if (percent >= 85) return { label: 'Отлично', state: 'excellent' };
        if (percent >= 70) return { label: 'Хорошо', state: 'good' };
        if (percent >= 50) return { label: 'Удовлетворительно', state: 'satisfactory' };
        return { label: 'Здесь появится твоя оценка', state: 'pending' };
    }

    function buildCourseGradeDemoMeta(config, stepCount) {
        var steps = (config && config.steps) || [];
        var limit = Math.max(0, Math.min(steps.length, Math.round(Number(stepCount) || 0)));
        var moduleDone = {};
        var moduleTotal = {};
        var topicDone = {};
        var topicTotal = {};
        var projectStagesByModule = {};
        var taskDone = 0;

        steps.forEach(function (step) {
            var key = String(step.module || '');
            moduleTotal[key] = (moduleTotal[key] || 0) + 1;
            if (step.topic != null) {
                var topicKey = key + ':' + String(step.topic);
                topicTotal[topicKey] = (topicTotal[topicKey] || 0) + 1;
            }
        });

        steps.slice(0, limit).forEach(function (step) {
            var key = String(step.module || '');
            moduleDone[key] = (moduleDone[key] || 0) + 1;
            if (step.topic != null) {
                var topicKey = key + ':' + String(step.topic);
                topicDone[topicKey] = (topicDone[topicKey] || 0) + 1;
            }
            if (step.isProject && step.projectStage != null) {
                if (!projectStagesByModule[key]) projectStagesByModule[key] = {};
                projectStagesByModule[key][String(step.projectStage)] = true;
            } else {
                taskDone += 1;
            }
        });

        var percent = 0;
        Object.keys((config && config.projectWeights) || {}).forEach(function (key) {
            var total = Number((config.projectStageTotals || {})[key]) || 0;
            var done = Object.keys(projectStagesByModule[key] || {}).length;
            if (total) percent += Math.floor(done * Number(config.projectWeights[key] || 0) / total);
        });

        var taskTotal = Number(config && config.taskTotal) || 0;
        if (taskTotal) percent += Math.floor(taskDone * Number(config.taskWeight || 0) / taskTotal);
        percent = Math.max(0, Math.min(100, percent));

        var grade = courseGradeLabel(percent);
        return {
            stepCount: limit,
            stepsTotal: steps.length,
            percent: percent,
            label: grade.label,
            state: grade.state,
            moduleDone: moduleDone,
            moduleTotal: moduleTotal,
            topicDone: topicDone,
            topicTotal: topicTotal,
            projectStagesByModule: projectStagesByModule
        };
    }

    function setWidth(el, percent) {
        if (el) el.style.width = percent + '%';
    }

    function applyHomeCourseGradeDemo() {
        if (!document.body.classList.contains('page-home')) return;
        var config = readCourseGradeDemoConfig();
        if (!config) return;
        var stored = readCourseGradeDemoStepCount(config);
        if (stored === null) return;

        var meta = buildCourseGradeDemoMeta(config, stored);
        var overallPct = meta.stepsTotal ? Math.round(meta.stepCount * 100 / meta.stepsTotal) : 0;

        setWidth(document.querySelector('[data-home-progress-fill]'), overallPct);
        var progressValue = document.querySelector('[data-home-progress-value]');
        if (progressValue) progressValue.textContent = meta.stepCount + ' / ' + meta.stepsTotal + ' заданий';
        var progressHint = document.querySelector('[data-home-progress-hint]');
        if (progressHint) progressHint.textContent = overallPct + '% курса пройдено';

        var gradeCard = document.querySelector('[data-home-grade-card]');
        if (gradeCard) {
            gradeCard.classList.remove(
                'stat-card--grade-pending',
                'stat-card--grade-satisfactory',
                'stat-card--grade-good',
                'stat-card--grade-excellent'
            );
            gradeCard.classList.add('stat-card--grade-' + meta.state);
        }
        var gradeLabel = document.querySelector('[data-home-grade-label]');
        if (gradeLabel) gradeLabel.textContent = meta.label;
        setWidth(document.querySelector('[data-home-grade-fill]'), meta.percent);
        var gradeHint = document.querySelector('[data-home-grade-hint]');
        if (gradeHint) gradeHint.textContent = meta.percent + '% до итоговой оценки';

        document.querySelectorAll('[data-home-module]').forEach(function (tile) {
            var key = String(tile.getAttribute('data-home-module') || '');
            var total = meta.moduleTotal[key] || 0;
            var done = meta.moduleDone[key] || 0;
            var pct = total ? Math.round(done * 100 / total) : 0;
            setWidth(tile.querySelector('[data-home-module-fill]'), pct);
            var pctEl = tile.querySelector('[data-home-module-pct]');
            if (pctEl) pctEl.textContent = pct + '%';
        });

        document.querySelectorAll('[data-ach-card]').forEach(function (card) {
            var minCompleted = card.getAttribute('data-ach-min-completed');
            var minFraction = card.getAttribute('data-ach-min-fraction');
            var topicModule = card.getAttribute('data-ach-topic-module');
            var topicNum = card.getAttribute('data-ach-topic-num');
            var projectModule = card.getAttribute('data-ach-project-module');
            var unlocked = false;
            if (minCompleted !== null) {
                unlocked = meta.stepCount >= Number(minCompleted);
            } else if (minFraction !== null) {
                unlocked = meta.stepsTotal > 0 && meta.stepCount / meta.stepsTotal >= Number(minFraction) - 1e-9;
            } else if (topicModule !== null && topicNum !== null) {
                var topicKey = String(topicModule) + ':' + String(topicNum);
                var topicTotal = meta.topicTotal[topicKey] || 0;
                unlocked = topicTotal > 0 && (meta.topicDone[topicKey] || 0) >= topicTotal;
            } else if (projectModule !== null) {
                var projectKey = String(projectModule);
                var projectTotal = Number((config.projectStageTotals || {})[projectKey]) || 0;
                var projectDone = Object.keys(meta.projectStagesByModule[projectKey] || {}).length;
                unlocked = projectTotal > 0 && projectDone >= projectTotal;
            }
            card.classList.toggle('ach-card--locked', !unlocked);
            var badge = card.querySelector('[data-ach-badge]');
            if (badge) {
                badge.textContent = unlocked ? 'Получено' : 'Закрыто';
                badge.classList.toggle('ach-card__badge--muted', !unlocked);
            }
        });
    }

    function initLearnShellDrawers() {
        var body = document.body;
        if (!body.classList.contains('page-learn')) return;

        var backdrop = document.getElementById('learnNavBackdrop');
        var left = document.getElementById('learnSidebarLeft');
        var right = document.getElementById('learnSidebarRight');
        var openLeft = document.getElementById('learnOpenLeft');
        var openRight = document.getElementById('learnOpenRight');
        var closeLeft = document.getElementById('learnCloseLeft');
        var closeRight = document.getElementById('learnCloseRight');

        if (!backdrop || !left || !right) return;

        var lastFocus = null;

        function isDrawerLayout() {
            return global.matchMedia && global.matchMedia('(max-width: 900px)').matches;
        }

        function setBackdrop(on) {
            if (on) {
                backdrop.classList.add('is-visible');
                backdrop.setAttribute('aria-hidden', 'false');
            } else {
                backdrop.classList.remove('is-visible');
                backdrop.setAttribute('aria-hidden', 'true');
            }
        }

        function closeAll() {
            left.classList.remove('learn-sidebar--open');
            right.classList.remove('learn-sidebar--open');
            setBackdrop(false);
            body.classList.remove('learn-drawer-open');
            if (openLeft) openLeft.setAttribute('aria-expanded', 'false');
            if (openRight) openRight.setAttribute('aria-expanded', 'false');
            if (lastFocus && typeof lastFocus.focus === 'function') {
                try {
                    lastFocus.focus();
                } catch (e) {}
                lastFocus = null;
            }
        }

        function openSide(which) {
            if (!isDrawerLayout()) return;
            lastFocus = document.activeElement;
            if (which === 'left') {
                left.classList.add('learn-sidebar--open');
                right.classList.remove('learn-sidebar--open');
                if (openLeft) openLeft.setAttribute('aria-expanded', 'true');
                if (openRight) openRight.setAttribute('aria-expanded', 'false');
            } else {
                right.classList.add('learn-sidebar--open');
                left.classList.remove('learn-sidebar--open');
                if (openRight) openRight.setAttribute('aria-expanded', 'true');
                if (openLeft) openLeft.setAttribute('aria-expanded', 'false');
            }
            setBackdrop(true);
            body.classList.add('learn-drawer-open');
        }

        function onOpenLeft(e) {
            e.preventDefault();
            if (!isDrawerLayout()) return;
            if (left.classList.contains('learn-sidebar--open')) closeAll();
            else openSide('left');
        }

        function onOpenRight(e) {
            e.preventDefault();
            if (!isDrawerLayout()) return;
            if (right.classList.contains('learn-sidebar--open')) closeAll();
            else openSide('right');
        }

        if (openLeft) openLeft.addEventListener('click', onOpenLeft);
        if (openRight) openRight.addEventListener('click', onOpenRight);
        if (closeLeft) closeLeft.addEventListener('click', closeAll);
        if (closeRight) closeRight.addEventListener('click', closeAll);
        backdrop.addEventListener('click', closeAll);

        document.addEventListener('keydown', function (e) {
            if (e.key === 'Escape' && body.classList.contains('learn-drawer-open')) {
                closeAll();
            }
        });

        left.addEventListener('click', function (e) {
            if (!isDrawerLayout()) return;
            var t = e.target;
            if (t && t.closest && t.closest('a[href]')) closeAll();
        });

        right.addEventListener('click', function (e) {
            if (!isDrawerLayout()) return;
            var t = e.target;
            if (t && t.closest && t.closest('a[href], .module-row[role="button"]')) closeAll();
        });

        global.addEventListener(
            'resize',
            function () {
                if (!isDrawerLayout()) closeAll();
            },
            { passive: true }
        );
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function () {
            initLearnShellDrawers();
            applyHomeCourseGradeDemo();
        });
    } else {
        initLearnShellDrawers();
        applyHomeCourseGradeDemo();
    }
})(window);
