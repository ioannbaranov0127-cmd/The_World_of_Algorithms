(function () {
    var cfg = {};
    var saveDebounceTimer = null;
    var lastStdinForCheck = '';
    var interactiveRunId = null;
    var waitingInput = false;
    var activeTerminalDocKeyHandler = null;
    var interactivePollTimer = null;
    var interactivePollInFlight = false;
    var LEARN_SCROLL_KEY = 'learnScrollToTop';
    var LEARN_PAGE_SCROLL_KEY = 'learn-page-scroll-top';
    var LEARN_READING_MODE_KEY = 'learn-reading-mode';
    var LEARN_PANEL_VISIBILITY_KEY = 'learn-panel-visibility';
    var learnPageScrollTimer = null;

    function markLearnScrollToTop() {
        try {
            sessionStorage.setItem(LEARN_SCROLL_KEY, '1');
            localStorage.removeItem(LEARN_PAGE_SCROLL_KEY);
        } catch (e) {}
    }

    function scrollLearnPageToTop() {
        try {
            window.scrollTo(0, 0);
            requestAnimationFrame(function () {
                window.scrollTo(0, 0);
            });
            setTimeout(function () {
                window.scrollTo(0, 0);
            }, 80);
        } catch (e) {
            window.scrollTo(0, 0);
        }
    }

    function applyLearnScrollOnLoad() {
        try {
            if (sessionStorage.getItem(LEARN_SCROLL_KEY)) {
                sessionStorage.removeItem(LEARN_SCROLL_KEY);
                localStorage.removeItem(LEARN_PAGE_SCROLL_KEY);
                if ('scrollRestoration' in history) history.scrollRestoration = 'manual';
                scrollLearnPageToTop();
                return true;
            }
        } catch (e) {}
        return false;
    }

    function saveLearnPageScroll() {
        try {
            if (sessionStorage.getItem(LEARN_SCROLL_KEY)) return;
            localStorage.setItem(LEARN_PAGE_SCROLL_KEY, String(window.scrollY || 0));
        } catch (e) {}
    }

    function restoreLearnPageScroll() {
        try {
            var raw = localStorage.getItem(LEARN_PAGE_SCROLL_KEY);
            if (raw == null) return;
            var value = parseInt(raw, 10);
            if (Number.isNaN(value)) return;
            if ('scrollRestoration' in history) history.scrollRestoration = 'manual';
            requestAnimationFrame(function () {
                window.scrollTo(0, value);
            });
        } catch (e) {}
    }

    function initLearnPageScrollMemory(skipRestore) {
        if (!skipRestore) restoreLearnPageScroll();
        if (window._learnPageScrollMemoryBound) return;
        window._learnPageScrollMemoryBound = true;
        window.addEventListener('scroll', function () {
            clearTimeout(learnPageScrollTimer);
            learnPageScrollTimer = setTimeout(saveLearnPageScroll, 120);
        }, { passive: true });
        window.addEventListener('beforeunload', saveLearnPageScroll);
    }

    function reloadLearnPage(scrollOnTopicChange) {
        if (scrollOnTopicChange) {
            markLearnScrollToTop();
            window.location.href = '/learn';
            return;
        }
        location.reload();
    }

    function refreshLearnTaskInPlace() {
        abortInteractive(true);
        if (window.LearnCodeEditor && window.LearnCodeEditor.destroy) {
            window.LearnCodeEditor.destroy();
        }
        clearTimeout(saveDebounceTimer);
        lastStdinForCheck = '';
        var prevTopicId = cfg.currentTopicId || '';
        var scrollAnchor = window.scrollY;
        return fetch(window.location.pathname + window.location.search, {
            credentials: 'same-origin',
            headers: { 'Cache-Control': 'no-cache' },
        })
            .then(function (r) {
                return r.text();
            })
            .then(function (html) {
                var doc = new DOMParser().parseFromString(html, 'text/html');
                var newCfgEl = doc.getElementById('learn-config');
                if (newCfgEl) {
                    var nextCfg;
                    try {
                        nextCfg = JSON.parse(newCfgEl.textContent);
                    } catch (e) {
                        nextCfg = null;
                    }
                    if (nextCfg && nextCfg.currentTopicId && prevTopicId && nextCfg.currentTopicId !== prevTopicId) {
                        markLearnScrollToTop();
                        window.location.href = '/learn';
                        return;
                    }
                }
                var newDyn = doc.getElementById('learn-dynamic-content');
                var curDyn = document.getElementById('learn-dynamic-content');
                if (!newDyn || !curDyn) {
                    location.reload();
                    return;
                }
                curDyn.innerHTML = newDyn.innerHTML;
                var newPill = doc.querySelector('.task-pill');
                var curPill = document.querySelector('.task-pill');
                if (newPill && curPill) curPill.innerHTML = newPill.innerHTML;
                var elCfg = document.getElementById('learn-config');
                if (elCfg && newCfgEl) {
                    elCfg.textContent = newCfgEl.textContent;
                    cfg = JSON.parse(elCfg.textContent);
                    if (cfg.projectMeta) applyProjectMeta(cfg.projectMeta);
                }
                initReadingModeToggle();
                initPanelVisibilityToggle();
                bindLearnTaskUi();
                updateTopicTaskNav();
                if (window.scrollY !== scrollAnchor) {
                    window.scrollTo(0, scrollAnchor);
                }
            });
    }

    function isTopicChangedNav(data) {
        if (!data) return false;
        var cur = data.current_topic_id;
        var nxt = data.next_topic_id;
        if (cur != null && cur !== '' && nxt != null && nxt !== '') {
            return String(cur) !== String(nxt);
        }
        return data.topic_changed === true;
    }

    function handleTaskNavResponse(data) {
        if (!data || !data.success) return;
        if (isTopicChangedNav(data)) {
            markLearnScrollToTop();
            window.location.href = '/learn';
            return;
        }
        refreshLearnTaskInPlace().catch(function () {
            location.reload();
        });
    }

    function updateTopicTaskNav() {
        var nav = document.getElementById('topicTaskNav');
        if (!nav) return;
        var activeId = cfg.currentTaskId;
        var tasks = cfg.topicTasks || [];
        nav.querySelectorAll('[data-task-id]').forEach(function (btn) {
            var tid = parseInt(btn.getAttribute('data-task-id'), 10);
            var meta = null;
            for (var i = 0; i < tasks.length; i++) {
                if (tasks[i].id === tid) {
                    meta = tasks[i];
                    break;
                }
            }
            var isActive = tid === activeId;
            btn.classList.toggle('topic-task-nav__item--active', isActive);
            btn.classList.toggle('topic-task-nav__item--done', !!(meta && meta.done));
            btn.setAttribute('aria-selected', isActive ? 'true' : 'false');
            btn.setAttribute('aria-current', isActive ? 'step' : 'false');
        });
    }

    function markCurrentTopicTaskDone(taskId) {
        if (!cfg.topicTasks) return;
        for (var i = 0; i < cfg.topicTasks.length; i++) {
            if (cfg.topicTasks[i].id === taskId) {
                cfg.topicTasks[i].done = true;
                break;
            }
        }
        updateTopicTaskNav();
    }

    function gotoTopicTask(taskId) {
        if (taskId === cfg.currentTaskId) return;
        saveCodeToStorage();
        fetch('/goto_task', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ task_id: taskId }),
        })
            .then(function (r) {
                return r.json();
            })
            .then(function (data) {
                if (!data.success) {
                    showNotification(data.message || 'Не удалось перейти к заданию', 'error');
                    return;
                }
                handleTaskNavResponse(data);
            })
            .catch(function () {
                showNotification('Сеть недоступна', 'error');
            });
    }

    function bindTopicTaskNav() {
        var nav = document.getElementById('topicTaskNav');
        if (!nav || nav.dataset.bound === '1') return;
        nav.dataset.bound = '1';
        nav.addEventListener('click', function (e) {
            var btn = e.target.closest('[data-task-id]');
            if (!btn) return;
            var tid = parseInt(btn.getAttribute('data-task-id'), 10);
            if (!tid || tid === cfg.currentTaskId) return;
            gotoTopicTask(tid);
        });
    }

    function bindSchemeLightbox() {
        var box = document.getElementById('schemeLightbox');
        if (!box || box.dataset.bound === '1') return;
        box.dataset.bound = '1';

        var img = document.getElementById('schemeLightboxImg');
        var title = document.getElementById('schemeLightboxTitle');
        var caption = document.getElementById('schemeLightboxCaption');
        var viewport = box.querySelector('.scheme-lightbox__viewport');
        var percentBtn = box.querySelector('[data-scheme-zoom="reset"]');
        var zoom = 1;

        function getFitZoom() {
            if (!img || !viewport || !img.naturalWidth || !img.naturalHeight) return 1;
            var availableWidth = Math.max(1, viewport.clientWidth - 4);
            var availableHeight = Math.max(1, viewport.clientHeight - 4);
            var widthZoom = availableWidth / img.naturalWidth;
            var heightZoom = availableHeight / img.naturalHeight;
            return Math.min(1, widthZoom, heightZoom);
        }

        function applyZoom(nextZoom) {
            zoom = Math.max(0.15, Math.min(4, nextZoom));
            if (img) img.style.width = zoom * 100 + '%';
            if (percentBtn) percentBtn.textContent = Math.round(zoom * 100) + '%';
        }

        function fitToViewport() {
            applyZoom(getFitZoom());
        }

        function openLightbox(src, text) {
            if (!img) return;
            img.src = src;
            img.alt = text || 'Схема';
            if (title) title.textContent = text || 'Схема';
            if (caption) caption.textContent = text || '';
            box.hidden = false;
            document.body.classList.add('scheme-lightbox-open');
            if (img.complete) fitToViewport();
            else img.onload = fitToViewport;
            var closeBtn = box.querySelector('[data-scheme-close]');
            if (closeBtn) closeBtn.focus();
        }

        function closeLightbox() {
            box.hidden = true;
            document.body.classList.remove('scheme-lightbox-open');
            if (img) {
                img.removeAttribute('src');
                img.style.width = '';
            }
        }

        document.addEventListener('click', function (e) {
            var trigger = e.target.closest('.theory-scheme-zoom-trigger');
            if (!trigger) return;
            e.preventDefault();
            openLightbox(trigger.getAttribute('data-scheme-src'), trigger.getAttribute('data-scheme-caption'));
        });

        box.addEventListener('click', function (e) {
            if (e.target.closest('[data-scheme-close]')) {
                closeLightbox();
                return;
            }
            var control = e.target.closest('[data-scheme-zoom]');
            if (!control) return;
            var action = control.getAttribute('data-scheme-zoom');
            if (action === 'in') applyZoom(zoom + 0.25);
            else if (action === 'out') applyZoom(zoom - 0.25);
            else if (action === 'fit') fitToViewport();
            else applyZoom(1);
        });

        document.addEventListener('keydown', function (e) {
            if (box.hidden) return;
            if (e.key === 'Escape') closeLightbox();
            else if (e.key === '+' || e.key === '=') applyZoom(zoom + 0.25);
            else if (e.key === '-' || e.key === '_') applyZoom(zoom - 0.25);
            else if (e.key === '0') applyZoom(1);
            else if (e.key.toLowerCase() === 'f') fitToViewport();
        });

        window.addEventListener('resize', function () {
            if (box.hidden) return;
            if (zoom <= getFitZoom() + 0.02) fitToViewport();
        });
    }

    var SIDEBAR_MODULES_KEY = 'learn-sidebar-modules-expanded';
    var LEFT_SIDEBAR_SCROLL_KEY = 'learn-left-sidebar-scroll-top';
    var RIGHT_SIDEBAR_SCROLL_KEY = 'learn-right-sidebar-scroll-top';
    var COURSE_GRADE_DEMO_KEY = 'learn-course-grade-demo-step-count';
    var COURSE_GRADE_DEMO_OLD_KEY = 'learn-course-grade-demo-percent';
    var leftSidebarScrollTimer = null;
    var rightSidebarScrollTimer = null;

    function readSidebarModulesState() {
        try {
            var raw = localStorage.getItem(SIDEBAR_MODULES_KEY);
            if (!raw) return null;
            var parsed = JSON.parse(raw);
            return parsed && typeof parsed === 'object' ? parsed : null;
        } catch (e) {
            return null;
        }
    }

    function writeSidebarModulesState(state) {
        try {
            localStorage.setItem(SIDEBAR_MODULES_KEY, JSON.stringify(state));
        } catch (e) {}
    }

    function collectSidebarModulesStateFromDom() {
        var state = {};
        document.querySelectorAll('.sidebar-module[data-module-id]').forEach(function (section) {
            state[section.dataset.moduleId] = !section.classList.contains('sidebar-module--collapsed');
        });
        return state;
    }

    function applySidebarModulesState(state) {
        if (!state) return;
        document.querySelectorAll('.sidebar-module[data-module-id]').forEach(function (section) {
            var id = section.dataset.moduleId;
            if (!Object.prototype.hasOwnProperty.call(state, id)) return;
            var expanded = !!state[id];
            section.classList.toggle('sidebar-module--collapsed', !expanded);
            var btn = section.querySelector('.sidebar-module__toggle');
            if (btn) btn.setAttribute('aria-expanded', expanded ? 'true' : 'false');
        });
    }

    function saveSidebarScroll(sidebar, key) {
        if (!sidebar) return;
        try {
            localStorage.setItem(key, String(sidebar.scrollTop || 0));
        } catch (e) {}
    }

    function restoreSidebarScroll(sidebar, key) {
        if (!sidebar) return;
        try {
            var raw = localStorage.getItem(key);
            if (raw == null) return;
            var value = parseInt(raw, 10);
            if (Number.isNaN(value)) return;
            requestAnimationFrame(function () {
                sidebar.scrollTop = value;
            });
        } catch (e) {}
    }

    function initSidebarScrollMemory(sidebarId, key, timerName) {
        var sidebar = document.getElementById(sidebarId);
        if (!sidebar || sidebar.dataset.scrollMemoryBound) return;
        sidebar.dataset.scrollMemoryBound = '1';

        restoreSidebarScroll(sidebar, key);
        sidebar.addEventListener('scroll', function () {
            if (timerName === 'right') {
                clearTimeout(rightSidebarScrollTimer);
                rightSidebarScrollTimer = setTimeout(function () {
                    saveSidebarScroll(sidebar, key);
                }, 120);
                return;
            }
            clearTimeout(leftSidebarScrollTimer);
            leftSidebarScrollTimer = setTimeout(function () {
                saveSidebarScroll(sidebar, key);
            }, 120);
        });
        window.addEventListener('beforeunload', function () {
            saveSidebarScroll(sidebar, key);
        });
    }

    function initSidebarsScrollMemory() {
        initSidebarScrollMemory('learnSidebarLeft', LEFT_SIDEBAR_SCROLL_KEY, 'left');
        initSidebarScrollMemory('learnSidebarRight', RIGHT_SIDEBAR_SCROLL_KEY, 'right');
    }

    function initSidebarModules() {
        var saved = readSidebarModulesState();
        if (saved) applySidebarModulesState(saved);

        document.querySelectorAll('.sidebar-module__toggle').forEach(function (btn) {
            if (btn.dataset.bound) return;
            btn.dataset.bound = '1';
            btn.addEventListener('click', function () {
                var section = btn.closest('.sidebar-module');
                if (!section) return;
                var collapsed = section.classList.toggle('sidebar-module--collapsed');
                btn.setAttribute('aria-expanded', collapsed ? 'false' : 'true');
                writeSidebarModulesState(collectSidebarModulesStateFromDom());
                saveSidebarScroll(document.getElementById('learnSidebarLeft'), LEFT_SIDEBAR_SCROLL_KEY);
            });
        });
    }

    function initLearnNavigationScroll() {
        var forcedTop = applyLearnScrollOnLoad();
        initLearnPageScrollMemory(forcedTop);

        document.querySelectorAll('.topic-sidebar-nav__link[href]').forEach(function (link) {
            link.addEventListener('click', function () {
                if (!link.classList.contains('topic-sidebar-nav__link--active')) {
                    markLearnScrollToTop();
                }
            });
        });
    }

    function setReadingMode(enabled) {
        document.body.classList.toggle('learn-reading-mode', enabled);
        var btn = document.getElementById('readingModeBtn');
        if (btn) {
            btn.setAttribute('aria-pressed', enabled ? 'true' : 'false');
            btn.setAttribute('aria-label', enabled ? 'Вернуть обычный режим' : 'Включить режим чтения');
            btn.setAttribute('title', enabled ? 'Обычный режим' : 'Режим чтения');
            var text = btn.querySelector('.reading-mode-toggle__text');
            if (text) text.textContent = enabled ? 'Обычный режим' : 'Режим чтения';
        }
        try {
            localStorage.setItem(LEARN_READING_MODE_KEY, enabled ? '1' : '0');
        } catch (e) {}
        if (enabled) {
            document.querySelectorAll('.learn-sidebar--open').forEach(function (panel) {
                panel.classList.remove('learn-sidebar--open');
            });
            var backdrop = document.getElementById('learnNavBackdrop');
            if (backdrop) backdrop.classList.remove('is-visible');
            document.body.classList.remove('learn-drawer-open');
        }
        updatePanelVisibilityAvailability(enabled);
    }

    function updatePanelVisibilityAvailability(readingModeEnabled) {
        var root = document.getElementById('panelVisibilityToggle');
        if (!root) return;
        root.classList.toggle('panel-visibility-toggle--disabled', readingModeEnabled);
        root.querySelectorAll('[data-panel-toggle]').forEach(function (btn) {
            btn.disabled = readingModeEnabled;
        });
    }

    function initReadingModeToggle() {
        var btn = document.getElementById('readingModeBtn');
        if (!btn || btn.dataset.bound === '1') return;
        btn.dataset.bound = '1';
        var enabled = false;
        try {
            enabled = localStorage.getItem(LEARN_READING_MODE_KEY) === '1';
        } catch (e) {}
        setReadingMode(enabled);
        btn.addEventListener('click', function () {
            setReadingMode(!document.body.classList.contains('learn-reading-mode'));
        });
    }

    function readPanelVisibilityState() {
        try {
            var parsed = JSON.parse(localStorage.getItem(LEARN_PANEL_VISIBILITY_KEY) || '{}');
            return {
                leftHidden: !!parsed.leftHidden,
                rightHidden: !!parsed.rightHidden
            };
        } catch (e) {
            return { leftHidden: false, rightHidden: false };
        }
    }

    function savePanelVisibilityState(state) {
        try {
            localStorage.setItem(LEARN_PANEL_VISIBILITY_KEY, JSON.stringify({
                leftHidden: !!state.leftHidden,
                rightHidden: !!state.rightHidden
            }));
        } catch (e) {}
    }

    function setPanelVisibilityState(state, persist) {
        var leftHidden = !!state.leftHidden;
        var rightHidden = !!state.rightHidden;

        document.body.classList.toggle('learn-hide-left-panel', leftHidden);
        document.body.classList.toggle('learn-hide-right-panel', rightHidden);

        document.querySelectorAll('[data-panel-toggle]').forEach(function (btn) {
            var side = btn.dataset.panelToggle;
            var hidden = side === 'left' ? leftHidden : rightHidden;
            var stateEl = btn.querySelector('.panel-visibility-toggle__state');
            btn.setAttribute('aria-pressed', hidden ? 'true' : 'false');
            btn.setAttribute('aria-label', (hidden ? 'Показать ' : 'Скрыть ') + (side === 'left' ? 'левую панель' : 'правую панель'));
            btn.setAttribute('title', (hidden ? 'Показать ' : 'Скрыть ') + (side === 'left' ? 'левую панель' : 'правую панель'));
            if (stateEl) stateEl.textContent = hidden ? '+' : '−';
        });

        if (persist) savePanelVisibilityState({ leftHidden: leftHidden, rightHidden: rightHidden });
    }

    function initPanelVisibilityToggle() {
        var root = document.getElementById('panelVisibilityToggle');
        if (!root || root.dataset.bound === '1') return;
        root.dataset.bound = '1';

        var state = readPanelVisibilityState();
        setPanelVisibilityState(state, false);
        updatePanelVisibilityAvailability(document.body.classList.contains('learn-reading-mode'));

        root.querySelectorAll('[data-panel-toggle]').forEach(function (btn) {
            btn.addEventListener('click', function () {
                var current = readPanelVisibilityState();
                if (btn.dataset.panelToggle === 'left') {
                    current.leftHidden = !current.leftHidden;
                } else {
                    current.rightHidden = !current.rightHidden;
                }
                setPanelVisibilityState(current, true);
            });
        });
    }

    function cleanupActiveTerminalDocKeyHandler() {
        if (!activeTerminalDocKeyHandler) return;
        document.removeEventListener('keydown', activeTerminalDocKeyHandler, true);
        activeTerminalDocKeyHandler = null;
    }

    function stopInteractivePolling() {
        if (interactivePollTimer) {
            clearInterval(interactivePollTimer);
            interactivePollTimer = null;
        }
        interactivePollInFlight = false;
    }

    function startInteractivePolling() {
        stopInteractivePolling();
        interactivePollTimer = setInterval(function () {
            if (!interactiveRunId || waitingInput || interactivePollInFlight) return;
            interactivePollInFlight = true;
            fetch('/interactive/poll', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ run_id: interactiveRunId }),
            })
                .then(function (r) {
                    return r.json().then(function (body) {
                        return { ok: r.ok, body: body };
                    });
                })
                .then(function (x) {
                    if (!x.ok || x.body.success === false) {
                        stopInteractivePolling();
                        return;
                    }
                    if (x.body.run_id && interactiveRunId && x.body.run_id !== interactiveRunId) return;
                    handleInteractivePhase(x.body);
                })
                .catch(function () {})
                .finally(function () {
                    interactivePollInFlight = false;
                });
        }, 120);
    }

    function codeStorageKey() {
        return 'code_task_' + cfg.currentTaskId;
    }

    function projectCodeStorageKey() {
        return 'project_code_m' + cfg.currentModule;
    }

    function saveProjectCodeToStorage(code) {
        try {
            localStorage.setItem(projectCodeStorageKey(), code != null ? String(code) : '');
        } catch (e) {}
    }

    function getProjectCodeFromStorage() {
        try {
            return localStorage.getItem(projectCodeStorageKey());
        } catch (e) {
            return null;
        }
    }

    function renderProjectChecklistItem(item) {
        var li = document.createElement('li');
        li.className = 'project-checklist__item project-checklist__item--' + (item.status || 'pending');
        li.setAttribute('data-stage', String(item.num));

        var mark = document.createElement('span');
        mark.className = 'project-checklist__mark';
        mark.setAttribute('aria-hidden', 'true');

        var row = document.createElement('div');
        row.className = 'project-checklist__head';

        var title = document.createElement('span');
        title.className = 'project-checklist__title';
        var ver = document.createElement('span');
        ver.className = 'project-checklist__ver';
        ver.textContent = item.version_label || item.version || '';
        title.appendChild(ver);
        title.appendChild(document.createTextNode(' ' + (item.feature || 'Шаг ' + item.num)));

        row.appendChild(title);
        li.appendChild(mark);
        li.appendChild(row);
        return li;
    }

    function applyProjectMeta(meta) {
        if (!meta) return;

        var card = document.getElementById('projectProgressCard');
        if (card) {
            card.classList.toggle('project-progress--complete', !!meta.is_complete);
        }

        var summary = document.querySelector('[data-project-summary]');
        if (summary && meta.stages_total != null) {
            var done = meta.stages_done_count || 0;
            var total = meta.stages_total;
            if (meta.is_complete) {
                summary.textContent = 'Проект готов';
            } else {
                summary.textContent = done + ' из ' + total + ' версий';
            }
        }

        var bar = document.querySelector('[data-project-bar]');
        if (bar && meta.stages_total) {
            var pct = Math.round(((meta.stages_done_count || 0) / meta.stages_total) * 100);
            bar.style.width = pct + '%';
        }

        var meter = document.querySelector('.project-progress__meter');
        if (meter && meta.stages_total != null) {
            meter.setAttribute('aria-valuenow', String(meta.stages_done_count || 0));
            meter.setAttribute('aria-valuemax', String(meta.stages_total));
        }

        var list = document.querySelector('[data-project-checklist]');
        if (list && meta.checklist && meta.checklist.length) {
            var shouldHighlightProjectStage = !!(
                cfg &&
                cfg.isProjectStage &&
                !cfg.isProjectStageLocked &&
                cfg.currentTopicNum != null
            );
            var targetStage = shouldHighlightProjectStage ? String(cfg.currentTopicNum) : null;

            list.innerHTML = '';
            for (var i = 0; i < meta.checklist.length; i++) {
                var item = Object.assign({}, meta.checklist[i]);
                var itemStage = String(item.num);
                if (shouldHighlightProjectStage) {
                    if (itemStage === targetStage && item.status !== 'done') {
                        item.status = 'current';
                    } else if (item.status === 'current') {
                        item.status = 'pending';
                    }
                } else if (item.status === 'current') {
                    item.status = 'pending';
                }
                list.appendChild(renderProjectChecklistItem(item));
            }

            var cur = list.querySelector('.project-checklist__item--current');
            if (cur) {
                cur.classList.add('project-checklist__item--pulse');
                setTimeout(function () {
                    cur.classList.remove('project-checklist__item--pulse');
                }, 1800);
            }
        }
    }

    function scheduleSaveCode() {
        clearTimeout(saveDebounceTimer);
        saveDebounceTimer = setTimeout(saveCodeToStorage, 280);
    }

    function getCodeValue() {
        if (window.LearnCodeEditor && window.LearnCodeEditor.getValue) {
            return window.LearnCodeEditor.getValue();
        }
        var ta = document.getElementById('codeInput');
        return ta ? ta.value : '';
    }

    function setCodeValue(val, resetHistory) {
        if (window.LearnCodeEditor && window.LearnCodeEditor.setValue) {
            window.LearnCodeEditor.setValue(val, resetHistory);
            return;
        }
        var ta = document.getElementById('codeInput');
        if (ta) ta.value = val != null ? String(val) : '';
    }

    function ensureCodeEditorReady() {
        return new Promise(function (resolve) {
            if (window.LearnCodeEditor && window.LearnCodeEditor.create) {
                resolve();
                return;
            }
            window.addEventListener(
                'learn-code-editor-ready',
                function () {
                    resolve();
                },
                { once: true }
            );
        });
    }

    function saveCodeToStorage() {
        localStorage.setItem(codeStorageKey(), getCodeValue());
    }

    function applyLevelUi(levelObj) {
        if (!levelObj) return;
        var ring = document.querySelector('[data-level-ring]');
        if (ring) ring.style.setProperty('--level-pct', levelObj.level_pct + '%');
        var lv = document.querySelector('[data-level-value]');
        if (lv) lv.textContent = String(levelObj.level);
        var xpEl = document.querySelector('[data-xp-sub]');
        if (xpEl) {
            xpEl.textContent = levelObj.xp_in_level + ' / ' + levelObj.xp_to_next + ' XP до след. уровня';
        }
    }

    function applyCourseGradeUi(grade) {
        if (!grade) return;
        var card = document.querySelector('[data-course-grade-card]');
        if (card) {
            card.classList.remove(
                'course-grade--pending',
                'course-grade--satisfactory',
                'course-grade--good',
                'course-grade--excellent'
            );
            card.classList.add('course-grade--' + (grade.state || 'pending'));
        }
        var label = document.querySelector('[data-course-grade-label]');
        if (label) label.textContent = grade.label || 'Здесь появится твоя оценка';
        var marker = document.querySelector('[data-course-grade-marker]');
        if (marker) marker.style.left = (grade.percent || 0) + '%';
        var fill = document.querySelector('[data-course-grade-fill]');
        if (fill) fill.style.width = (grade.percent || 0) + '%';
        var scale = document.querySelector('.course-grade__scale');
        if (scale) scale.setAttribute('aria-valuenow', String(grade.percent || 0));
    }

    function getCourseGradeLabel(percent) {
        if (percent >= 85) return { label: 'Отлично', state: 'excellent' };
        if (percent >= 70) return { label: 'Хорошо', state: 'good' };
        if (percent >= 50) return { label: 'Удовлетворительно', state: 'satisfactory' };
        return { label: 'Здесь появится твоя оценка', state: 'pending' };
    }

    function getCourseGradeDemoConfig() {
        return (cfg && cfg.courseGradeDemo) || {
            steps: [],
            projectWeights: {},
            projectStageTotals: {},
            taskWeight: 20,
            taskTotal: 0
        };
    }

    function clampCourseGradeDemoStep(count) {
        var steps = getCourseGradeDemoConfig().steps || [];
        return Math.max(0, Math.min(steps.length, Math.round(Number(count) || 0)));
    }

    function readCourseGradeDemoStepCount() {
        try {
            var raw = localStorage.getItem(COURSE_GRADE_DEMO_KEY);
            if (raw === null || raw === '') return null;
            var value = clampCourseGradeDemoStep(Number(raw));
            return value > 0 ? value : null;
        } catch (e) {
            return null;
        }
    }

    function getCourseGradeDemoMeta(stepCount) {
        var demo = getCourseGradeDemoConfig();
        var steps = demo.steps || [];
        var limit = clampCourseGradeDemoStep(stepCount);
        var projectStagesByModule = {};
        var moduleDone = {};
        var moduleTotal = {};
        var completedTaskIds = {};
        var taskDone = 0;

        steps.forEach(function (step) {
            var key = String(step.module || '');
            moduleTotal[key] = (moduleTotal[key] || 0) + 1;
        });

        steps.slice(0, limit).forEach(function (step) {
            var moduleKey = String(step.module || '');
            moduleDone[moduleKey] = (moduleDone[moduleKey] || 0) + 1;
            if (step.taskId != null) completedTaskIds[String(step.taskId)] = true;
            if (step.isProject && step.projectStage != null) {
                if (!projectStagesByModule[moduleKey]) projectStagesByModule[moduleKey] = {};
                projectStagesByModule[moduleKey][String(step.projectStage)] = true;
            } else {
                taskDone += 1;
            }
        });

        var pct = 0;
        Object.keys(demo.projectWeights || {}).forEach(function (moduleKey) {
            var stageTotal = Number((demo.projectStageTotals || {})[moduleKey]) || 0;
            var stageDoneMap = projectStagesByModule[moduleKey] || {};
            var stageDone = Object.keys(stageDoneMap).length;
            if (stageTotal) {
                pct += Math.floor(stageDone * Number(demo.projectWeights[moduleKey] || 0) / stageTotal);
            }
        });

        var taskTotal = Number(demo.taskTotal) || 0;
        if (taskTotal) {
            pct += Math.floor(taskDone * Number(demo.taskWeight || 0) / taskTotal);
        }

        pct = Math.max(0, Math.min(100, pct));
        var label = getCourseGradeLabel(pct);
        return {
            percent: pct,
            label: label.label,
            state: label.state,
            stepCount: limit,
            stepsTotal: steps.length,
            moduleDone: moduleDone,
            moduleTotal: moduleTotal,
            completedTaskIds: completedTaskIds,
            projectStagesByModule: projectStagesByModule
        };
    }

    function updateCourseGradeDemoValue(meta) {
        var valueEl = document.querySelector('[data-course-grade-demo-value]');
        if (valueEl) valueEl.textContent = meta.percent + '%';
    }

    function applyCourseGradeDemoModuleUi(meta) {
        Object.keys(meta.moduleTotal || {}).forEach(function (moduleKey) {
            var section = document.querySelector('.sidebar-module[data-module-id="' + moduleKey + '"]');
            if (!section) return;
            var done = meta.moduleDone[moduleKey] || 0;
            var total = meta.moduleTotal[moduleKey] || 0;
            var pct = total ? Math.round(done * 100 / total) : 0;
            var pp = section.querySelector('.progress-card__percent');
            var pf = section.querySelector('.sidebar-main-progress .duo-progress__fill');
            var stat = section.querySelector('.progress-card__stats > span:first-child');
            if (pp) pp.textContent = pct + '%';
            if (pf) pf.style.width = pct + '%';
            if (stat) stat.textContent = done + ' / ' + total + ' заданий';
        });
    }

    function applyCourseGradeDemoTopicTaskNav(meta) {
        if (!cfg || !cfg.topicTasks) return;
        var completed = meta.completedTaskIds || {};
        cfg.topicTasks.forEach(function (task) {
            if (task._realDone === undefined) task._realDone = !!task.done;
            task.done = !!task._realDone || !!completed[String(task.id)];
        });
        updateTopicTaskNav();
    }

    function applyCourseGradeDemoProjectUi(meta) {
        if (!cfg || !cfg.projectMeta) return;
        var moduleKey = String(cfg.currentModule || '');
        var doneMap = meta.projectStagesByModule[moduleKey] || {};
        var done = Object.keys(doneMap).length;
        var total = Number(cfg.projectMeta.stages_total) || Number((getCourseGradeDemoConfig().projectStageTotals || {})[moduleKey]) || 0;
        var complete = total > 0 && done >= total;

        var card = document.getElementById('projectProgressCard');
        if (card) card.classList.toggle('project-progress--complete', complete);

        var summary = document.querySelector('[data-project-summary]');
        if (summary && total) {
            summary.textContent = complete ? 'Проект готов' : done + ' из ' + total + ' версий';
        }

        var bar = document.querySelector('[data-project-bar]');
        if (bar && total) bar.style.width = Math.round(done * 100 / total) + '%';

        document.querySelectorAll('[data-project-checklist] [data-stage]').forEach(function (item) {
            var isDone = !!doneMap[String(item.dataset.stage)];
            item.classList.toggle('project-checklist__item--done', isDone);
            item.classList.toggle('project-checklist__item--pending', !isDone);
            item.classList.remove('project-checklist__item--current');
        });
    }

    function applyCourseGradeDemoStepCount(stepCount, persist) {
        var meta = getCourseGradeDemoMeta(stepCount);
        if (persist) {
            try {
                localStorage.setItem(COURSE_GRADE_DEMO_KEY, String(meta.stepCount));
                localStorage.removeItem(COURSE_GRADE_DEMO_OLD_KEY);
            } catch (e) {}
        }
        updateCourseGradeDemoValue(meta);
        applyCourseGradeUi(meta);
        applyCourseGradeDemoModuleUi(meta);
        applyCourseGradeDemoTopicTaskNav(meta);
        applyCourseGradeDemoProjectUi(meta);
    }

    function applyStoredCourseGradeDemo() {
        var stored = readCourseGradeDemoStepCount();
        if (stored !== null) applyCourseGradeDemoStepCount(stored, false);
    }

    function initCourseGradeDemoControls() {
        var root = document.querySelector('[data-course-grade-demo]');
        if (!root || root.dataset.bound) return;
        root.dataset.bound = '1';

        var stored = readCourseGradeDemoStepCount();
        var current = stored !== null ? stored : 0;
        if (stored !== null) {
            applyCourseGradeDemoStepCount(current, false);
        } else {
            updateCourseGradeDemoValue(getCourseGradeDemoMeta(0));
        }

        root.querySelectorAll('[data-course-grade-demo-step]').forEach(function (btn) {
            btn.addEventListener('click', function () {
                var step = Number(btn.dataset.courseGradeDemoStep) || 0;
                var base = readCourseGradeDemoStepCount();
                if (base === null) base = current;
                current = clampCourseGradeDemoStep(base + step);
                applyCourseGradeDemoStepCount(current, true);
            });
        });

        var reset = root.querySelector('[data-course-grade-demo-reset]');
        if (reset) {
            reset.addEventListener('click', function () {
                try {
                    localStorage.removeItem(COURSE_GRADE_DEMO_KEY);
                    localStorage.removeItem(COURSE_GRADE_DEMO_OLD_KEY);
                } catch (e) {}
                window.location.reload();
            });
        }
    }

    function applySessionPayload(d) {
        if (!d || !d.success) return;
        var xpSide = document.querySelector('[data-total-xp]');
        if (xpSide) xpSide.textContent = String(d.total_xp);
        var doneEl = document.querySelector('[data-completed-count]');
        if (doneEl) doneEl.textContent = d.completed_tasks + ' / ' + d.total_tasks;
        var modulesRoot = document.querySelector('.sidebar-modules');
        var mid = modulesRoot ? modulesRoot.dataset.currentModule : null;
        if (mid) {
            var section = document.querySelector('.sidebar-module[data-module-id="' + mid + '"]');
            if (section) {
                var pp = section.querySelector('.progress-card__percent');
                var pf = section.querySelector('.sidebar-main-progress .duo-progress__fill');
                if (pp) pp.textContent = d.module_progress + '%';
                if (pf) pf.style.width = d.module_progress + '%';
            }
        }
        if (d.level) applyLevelUi(d.level);
        if (d.course_grade) applyCourseGradeUi(d.course_grade);
        if (d.project_meta) applyProjectMeta(d.project_meta);
        applyStoredCourseGradeDemo();
    }

    function fetchSession() {
        fetch('/api/session?task_id=' + encodeURIComponent(cfg.currentTaskId))
            .then(function (r) {
                return r.json();
            })
            .then(applySessionPayload)
            .catch(function () {});
    }

    function el(tag, className, text) {
        var n = document.createElement(tag);
        if (className) n.className = className;
        if (text !== undefined && text !== null) n.textContent = text;
        return n;
    }

    function getConsoleBox() {
        return document.getElementById('runConsole');
    }

    function setConsoleStatus(mode, text) {
        var st = document.getElementById('consoleStatus');
        if (!st) return;
        var t = text != null ? String(text) : '';
        st.textContent = t;
        st.className = 'edu-console__status';
        if (t === '') {
            st.classList.add('edu-console__status--empty');
            return;
        }
        if (mode === 'run') st.classList.add('edu-console__status--run');
        else if (mode === 'input') st.classList.add('edu-console__status--input');
        else if (mode === 'done') st.classList.add('edu-console__status--done');
        else if (mode === 'err') st.classList.add('edu-console__status--err');
    }

    function clearRunConsole(box) {
        while (box.firstChild) box.removeChild(box.firstChild);
    }

    function renderIdleConsole() {
        var box = getConsoleBox();
        if (!box) return;
        box.className = 'edu-console edu-console--idle';
        clearRunConsole(box);
        var p = el('p', 'edu-console__placeholder');
        p.textContent = 'Нажмите «Выполнить» — вывод появится здесь.';
        box.appendChild(p);
        setConsoleStatus('', '');
    }

    function toggleStopBtn(show) {
        var b = document.getElementById('stopRunBtn');
        if (b) b.style.display = show ? '' : 'none';
    }

    function appendSysLine(html) {
        var box = getConsoleBox();
        if (!box) return;
        var stick = box.scrollHeight - box.scrollTop - box.clientHeight < 28;
        var d = document.createElement('div');
        d.className = 'edu-console__sys';
        d.innerHTML = html;
        box.appendChild(d);
        if (stick) box.scrollTop = box.scrollHeight;
    }

    function appendOutText(text) {
        if (!text) return;
        var box = getConsoleBox();
        if (!box) return;
        var stick = box.scrollHeight - box.scrollTop - box.clientHeight < 28;
        var last = box.lastElementChild;
        if (
            last &&
            last.classList &&
            last.classList.contains('edu-console__out') &&
            !last.classList.contains('edu-console__out--err') &&
            !last.classList.contains('edu-console__out--sealed')
        ) {
            last.textContent += text;
        } else {
            var pre = el('pre', 'edu-console__out');
            pre.textContent = text;
            box.appendChild(pre);
        }
        if (stick) box.scrollTop = box.scrollHeight;
    }

    function appendErrText(text) {
        if (!text) return;
        var box = getConsoleBox();
        if (!box) return;
        var stick = box.scrollHeight - box.scrollTop - box.clientHeight < 28;
        var last = box.lastElementChild;
        if (last && last.classList && last.classList.contains('edu-console__out--err')) {
            last.textContent += text;
        } else {
            var pre = el('pre', 'edu-console__out edu-console__out--err');
            pre.textContent = text;
            box.appendChild(pre);
        }
        if (stick) box.scrollTop = box.scrollHeight;
    }

    function removeActiveTerminalInput() {
        var box = getConsoleBox();
        if (!box) return;
        var w = box.querySelector('.term-active-input');
        if (w) w.remove();
    }

    function freezeTerminalLine(container, fullText) {
        var parent = container.parentNode;
        if (!parent) return;
        var pre = el('pre', 'edu-console__out edu-console__out--sealed');
        pre.textContent = fullText;
        parent.replaceChild(pre, container);
        var box = getConsoleBox();
        if (box) box.scrollTop = box.scrollHeight;
    }

    function makeEditSpan() {
        var edit = document.createElement('span');
        edit.className = 'term-edit term-edit--empty';
        edit.setAttribute('contenteditable', 'true');
        // Make it programmatically focusable in more browsers.
        edit.setAttribute('tabindex', '0');
        edit.setAttribute('spellcheck', 'false');
        edit.setAttribute('autocomplete', 'off');
        edit.setAttribute('role', 'textbox');

        function ensureTextForCaret() {
            // Some browsers don't create a native caret for truly empty contenteditable.
            // We keep a zero-width char internally so caret placement works.
            var raw = (edit.textContent || '').replace(/\u200b/g, '');
            if (raw.length === 0) {
                edit.textContent = '\u200b';
                edit.classList.remove('term-edit--empty');
            }
        }

        function restoreEmptyStateIfNeeded() {
            var raw = (edit.textContent || '').replace(/\u200b/g, '');
            if (raw.length === 0) {
                edit.textContent = '';
                edit.classList.add('term-edit--empty');
            }
        }

        function syncEmpty() {
            var raw = (edit.textContent || '').replace(/\u200b/g, '');
            if (raw.indexOf('\n') >= 0 || raw.indexOf('\r') >= 0) {
                edit.textContent = raw.replace(/[\r\n]+/g, '');
            }
            raw = edit.textContent || '';
            if (raw.length === 0) edit.classList.add('term-edit--empty');
            else edit.classList.remove('term-edit--empty');
        }
        edit.addEventListener('input', syncEmpty);
        edit.addEventListener('focus', function () {
            ensureTextForCaret();
        });
        edit.addEventListener('blur', function () {
            restoreEmptyStateIfNeeded();
        });
        edit.addEventListener('paste', function (e) {
            e.preventDefault();
            var t = '';
            try {
                t = e.clipboardData.getData('text/plain');
            } catch (err) {}
            t = (t || '').replace(/[\r\n]+/g, '');
            if (document.queryCommandSupported && document.queryCommandSupported('insertText')) {
                document.execCommand('insertText', false, t);
            } else {
                edit.textContent = (edit.textContent || '') + t;
            }
            syncEmpty();
        });
        return edit;
    }

    /**
     * Ввод как в терминале: промпт из stdout сразу с редактируемым продолжением (contenteditable), без отдельного input.
     */
    function showInputAwait(stdoutChunk, onSubmit) {
        var box = getConsoleBox();
        if (!box) return;
        // Avoid leaking document listeners across multiple input() steps.
        if (activeTerminalDocKeyHandler) {
            document.removeEventListener('keydown', activeTerminalDocKeyHandler, true);
            activeTerminalDocKeyHandler = null;
        }
        removeActiveTerminalInput();
        waitingInput = true;
        var chunk = stdoutChunk == null ? '' : String(stdoutChunk);
        var endsWithNl = chunk.length > 0 && chunk[chunk.length - 1] === '\n';
        var lines = chunk.split('\n');

        var container = document.createElement('div');
        container.className = 'term-active-input';

        if (endsWithNl) {
            for (var i = 0; i < lines.length - 1; i++) {
                var fl = el('div', 'term-frozen-line');
                fl.textContent = lines[i];
                container.appendChild(fl);
            }
            var row = el('div', 'term-input-row');
            var edit = makeEditSpan();
            row.appendChild(edit);
            container.appendChild(row);
        } else {
            for (var j = 0; j < lines.length - 1; j++) {
                var fl2 = el('div', 'term-frozen-line');
                fl2.textContent = lines[j];
                container.appendChild(fl2);
            }
            var last = lines[lines.length - 1];
            var row2 = el('div', 'term-input-row');
            var fix = el('span', 'term-prompt-fix');
            fix.textContent = last;
            fix.setAttribute('contenteditable', 'false');
            var edit2 = makeEditSpan();
            row2.appendChild(fix);
            row2.appendChild(edit2);
            container.appendChild(row2);
        }

        function getUserText() {
            var ed = container.querySelector('.term-edit');
            if (!ed) return '';
            return (ed.textContent || '').replace(/\u200b/g, '').replace(/[\r\n]/g, '');
        }

        function focusEdit() {
            var ed = container.querySelector('.term-edit');
            if (!ed) return;
            // Ensure the editor has text so caret placement works consistently.
            try {
                var raw = (ed.textContent || '').replace(/\u200b/g, '');
                if (raw.length === 0) {
                    ed.textContent = '\u200b';
                    ed.classList.remove('term-edit--empty');
                }
            } catch (e3) {}
            try {
                ed.focus({ preventScroll: true });
            } catch (e) {
                try { ed.focus(); } catch (e2) {}
            }
            // If focus was blocked, restore the visual caret state (CSS pseudo-caret).
            try {
                if (document.activeElement !== ed) {
                    ed.textContent = '';
                    ed.classList.add('term-edit--empty');
                    return;
                }
            } catch (e4) {}
            try {
                // Put caret at the end so typing starts immediately.
                var sel = window.getSelection();
                var range = document.createRange();
                sel.removeAllRanges();

                if (ed.firstChild && ed.firstChild.nodeType === 3) {
                    var ln = (ed.firstChild.nodeValue || '').length;
                    range.setStart(ed.firstChild, ln);
                    range.collapse(true);
                } else {
                    range.selectNodeContents(ed);
                    range.collapse(false);
                }

                sel.addRange(range);
            } catch (e2) {}
        }

        var submitted = false;

        function cleanupDocKeyHandler() {
            if (!activeTerminalDocKeyHandler) return;
            document.removeEventListener('keydown', activeTerminalDocKeyHandler, true);
            activeTerminalDocKeyHandler = null;
        }

        function submitUser() {
            if (submitted) return;
            submitted = true;
            waitingInput = false;

            var user = getUserText();
            freezeTerminalLine(container, chunk + user);
            cleanupDocKeyHandler();
            onSubmit(user);
        }

        function ensureCaretText(ed) {
            if (!ed) return;
            var raw = (ed.textContent || '').replace(/\u200b/g, '');
            if (raw.length === 0) {
                ed.textContent = '\u200b';
                ed.classList.remove('term-edit--empty');
            }
        }

        function placeCaretAtStart(ed) {
            if (!ed) return;
            try {
                var sel = window.getSelection();
                var range = document.createRange();
                sel.removeAllRanges();
                if (ed.firstChild && ed.firstChild.nodeType === 3) {
                    range.setStart(ed.firstChild, 0);
                    range.collapse(true);
                } else {
                    range.selectNodeContents(ed);
                    range.collapse(true);
                }
                sel.addRange(range);
            } catch (e) {}
        }

        function placeCaretAtEnd(ed) {
            if (!ed) return;
            try {
                var sel = window.getSelection();
                var range = document.createRange();
                sel.removeAllRanges();
                if (ed.firstChild && ed.firstChild.nodeType === 3) {
                    var ln = (ed.firstChild.nodeValue || '').length;
                    range.setStart(ed.firstChild, ln);
                    range.collapse(true);
                } else {
                    range.selectNodeContents(ed);
                    range.collapse(false);
                }
                sel.addRange(range);
            } catch (e) {}
        }

        // Fallback: if browser focus gets blocked (common with async UI),
        // redirect key input to the active inline editor anyway.
        activeTerminalDocKeyHandler = function (e) {
            if (submitted) return;
            var ed = container.querySelector('.term-edit');
            if (!ed) return;

            if (document.activeElement === ed) return;
            if (e.ctrlKey || e.metaKey || e.altKey) return;

            if (e.key === 'Enter') {
                e.preventDefault();
                submitUser();
                return;
            }

            if (e.key === 'Backspace') {
                e.preventDefault();
                ensureCaretText(ed);
                try { ed.focus({ preventScroll: true }); } catch (e2) { try { ed.focus(); } catch (e3) {} }
                placeCaretAtEnd(ed);

                var raw = (ed.textContent || '').replace(/\u200b/g, '');
                raw = raw.length ? raw.substring(0, raw.length - 1) : '';
                if (raw.length === 0) {
                    ed.textContent = '\u200b';
                    ed.classList.add('term-edit--empty');
                } else {
                    ed.textContent = raw;
                    ed.classList.remove('term-edit--empty');
                }
                placeCaretAtEnd(ed);
                return;
            }

            if (e.key === 'Tab') {
                e.preventDefault();
                ensureCaretText(ed);
                try { ed.focus({ preventScroll: true }); } catch (e4) { try { ed.focus(); } catch (e5) {} }
                var rawTab = (ed.textContent || '').replace(/\u200b/g, '');
                rawTab = rawTab + '    ';
                ed.textContent = rawTab;
                ed.classList.remove('term-edit--empty');
                placeCaretAtEnd(ed);
                return;
            }

            if (e.key === 'ArrowLeft' || e.key === 'Home') {
                e.preventDefault();
                ensureCaretText(ed);
                try { ed.focus({ preventScroll: true }); } catch (e6) { try { ed.focus(); } catch (e7) {} }
                placeCaretAtStart(ed);
                return;
            }

            if (e.key === 'ArrowRight' || e.key === 'End') {
                e.preventDefault();
                ensureCaretText(ed);
                try { ed.focus({ preventScroll: true }); } catch (e8) { try { ed.focus(); } catch (e9) {} }
                placeCaretAtEnd(ed);
                return;
            }

            if (e.key && e.key.length === 1) {
                e.preventDefault();
                ensureCaretText(ed);
                try { ed.focus({ preventScroll: true }); } catch (e10) { try { ed.focus(); } catch (e11) {} }
                var rawCh = (ed.textContent || '').replace(/\u200b/g, '');
                rawCh = rawCh + e.key;
                ed.textContent = rawCh;
                ed.classList.remove('term-edit--empty');
                placeCaretAtEnd(ed);
            }
        };

        document.addEventListener('keydown', activeTerminalDocKeyHandler, true);

        container.addEventListener(
            'keydown',
            function (e) {
                var t = e.target;
                if (!t.classList || !t.classList.contains('term-edit')) return;
                if (e.key === 'Enter') {
                    e.preventDefault();
                    submitUser();
                    return;
                }
                if (e.key === 'Tab') {
                    e.preventDefault();
                    if (document.queryCommandSupported && document.queryCommandSupported('insertText')) {
                        document.execCommand('insertText', false, '    ');
                    } else {
                        // Fallback for older browsers.
                        ensureCaretText(t);
                        var rawTab2 = (t.textContent || '').replace(/\u200b/g, '');
                        t.textContent = rawTab2 + '    ';
                        t.classList.remove('term-edit--empty');
                        placeCaretAtEnd(t);
                    }
                }

                // Terminal-like caret boundaries: prevent the caret from escaping
                // beyond the editable span (stable Backspace / arrows).
                if (e.key === 'ArrowLeft' || e.key === 'ArrowRight' || e.key === 'Home' || e.key === 'End' || e.key === 'Backspace' || e.key === 'Delete') {
                    var sel = window.getSelection();
                    if (!sel || sel.rangeCount === 0) return;
                    var range = sel.getRangeAt(0);
                    var sc = range.startContainer;
                    if (!sc || sc.nodeType !== 3) return;
                    if (!t.contains(sc)) return;

                    var offset = range.startOffset;
                    var len = (sc.nodeValue || '').length;
                    var atStart = offset <= 0;
                    var atEnd = offset >= len;

                    if (e.key === 'Home') {
                        e.preventDefault();
                        placeCaretAtStart(t);
                        return;
                    }
                    if (e.key === 'End') {
                        e.preventDefault();
                        placeCaretAtEnd(t);
                        return;
                    }

                    if ((e.key === 'ArrowLeft' || e.key === 'Backspace') && atStart) {
                        e.preventDefault();
                        placeCaretAtStart(t);
                        return;
                    }

                    if ((e.key === 'ArrowRight' || e.key === 'Delete') && atEnd) {
                        e.preventDefault();
                        placeCaretAtEnd(t);
                        return;
                    }
                }
            },
            true
        );
        container.addEventListener('mousedown', function (e) {
            var t = e.target;
            if (t && t.classList && t.classList.contains('term-edit')) return;
            requestAnimationFrame(focusEdit);
        });

        box.appendChild(container);
        box.scrollTop = box.scrollHeight;
        // rAF helps to focus after the DOM is painted.
        requestAnimationFrame(function () {
            requestAnimationFrame(focusEdit);
        });
    }

    function appendFriendlyBlock(friendly, rawStderr) {
        var box = getConsoleBox();
        if (!box || !friendly) return;
        var wrap = el('div', 'edu-console__friendly');
        wrap.appendChild(el('p', 'edu-console__friendly-title', friendly.title || 'Ошибка'));
        if (friendly.tips && friendly.tips.length) {
            var ul = document.createElement('ul');
            ul.className = 'edu-console__friendly-tips';
            for (var i = 0; i < friendly.tips.length; i++) {
                ul.appendChild(el('li', '', friendly.tips[i]));
            }
            wrap.appendChild(ul);
        }
        if (rawStderr) {
            var det = document.createElement('details');
            det.className = 'edu-console__details';
            var sm = el('summary', '', 'Показать подробности');
            det.appendChild(sm);
            var pre = el('pre', '', rawStderr);
            det.appendChild(pre);
            wrap.appendChild(det);
        }
        box.appendChild(wrap);
        box.scrollTop = box.scrollHeight;
    }

    function handleInteractivePhase(data) {
        if (data.success === false) {
            setConsoleStatus('err', '');
            appendSysLine(data.message || 'Ошибка');
            toggleStopBtn(false);
            stopInteractivePolling();
            interactiveRunId = null;
            waitingInput = false;
            cleanupActiveTerminalDocKeyHandler();
            return;
        }
        if (data.status === 'error') {
            setConsoleStatus('err', '');
            var em = el('div', 'edu-console__sys');
            em.textContent = data.message || 'Ошибка выполнения';
            var box = getConsoleBox();
            if (box) box.appendChild(em);
            toggleStopBtn(false);
            stopInteractivePolling();
            interactiveRunId = null;
            waitingInput = false;
            cleanupActiveTerminalDocKeyHandler();
            return;
        }
        if (data.run_id) interactiveRunId = data.run_id;

        if (data.status === 'need_input') {
            if (data.stderr_chunk) appendErrText(data.stderr_chunk);
            setConsoleStatus('input', '');
            toggleStopBtn(true);
            stopInteractivePolling();
            showInputAwait(data.stdout_chunk || '', function (line) {
                setConsoleStatus('run', '');
                fetch('/interactive/input', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ run_id: data.run_id, line: line }),
                })
                    .then(function (r) {
                        return r.json().then(function (body) {
                            return { ok: r.ok, body: body };
                        });
                    })
                    .then(function (x) {
                        if (!x.ok || x.body.success === false) {
                            showNotification(x.body.message || 'Запуск завершён', 'error');
                            toggleStopBtn(false);
                            stopInteractivePolling();
                            interactiveRunId = null;
                            waitingInput = false;
                            cleanupActiveTerminalDocKeyHandler();
                            return;
                        }
                        if (x.body.run_id && interactiveRunId && x.body.run_id !== interactiveRunId) return;
                        if (x.body.status === 'running') startInteractivePolling();
                        handleInteractivePhase(x.body);
                    })
                    .catch(function () {
                        showNotification('Сеть недоступна', 'error');
                        toggleStopBtn(false);
                    });
            });
            return;
        }

        if (data.stdout_chunk) appendOutText(data.stdout_chunk);
        if (data.stderr_chunk) appendErrText(data.stderr_chunk);

        if (data.status === 'done') {
            toggleStopBtn(false);
            stopInteractivePolling();
            interactiveRunId = null;
            waitingInput = false;
            cleanupActiveTerminalDocKeyHandler();
            lastStdinForCheck = data.stdin_for_check != null ? data.stdin_for_check : '';
            if (data.exit_code === 0) {
                setConsoleStatus('done', '');
                showNotification('Программа завершилась', 'success');
            } else {
                setConsoleStatus('err', '');
                showNotification('Программа остановилась с ошибкой', 'error');
                if (data.friendly) appendFriendlyBlock(data.friendly, data.stderr);
                else if (data.stderr) appendFriendlyBlock({ title: 'Что-то пошло не так', tips: [] }, data.stderr);
            }
            saveCodeToStorage();
            return;
        }

        if (data.status === 'running') {
            setConsoleStatus('run', '');
            toggleStopBtn(true);
            if (interactiveRunId && !waitingInput) startInteractivePolling();
            return;
        }

        if (data.status === 'need_poll') {
            if (interactiveRunId && !waitingInput) startInteractivePolling();
            return;
        }

        toggleStopBtn(false);
        stopInteractivePolling();
        interactiveRunId = null;
        waitingInput = false;
        cleanupActiveTerminalDocKeyHandler();
    }

    function abortInteractive(silent) {
        var rid = interactiveRunId;
        fetch('/interactive/abort', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ run_id: rid }),
        })
            .then(function () {
                return;
            })
            .catch(function () {});
        stopInteractivePolling();
        interactiveRunId = null;
        waitingInput = false;
        cleanupActiveTerminalDocKeyHandler();
        toggleStopBtn(false);
        setConsoleStatus('', '');
        removeActiveTerminalInput();
        renderIdleConsole();
        if (!silent) showNotification('Выполнение остановлено', 'info');
    }

    function runInteractiveExecute() {
        var box = getConsoleBox();
        if (!box) return;
        var code = getCodeValue();
        lastStdinForCheck = '';
        var previousRunId = interactiveRunId;
        box.className = 'edu-console';
        clearRunConsole(box);
        appendSysLine('<span class="edu-console__spinner" aria-hidden="true"></span>');
        setConsoleStatus('run', '');
        toggleStopBtn(true);
        stopInteractivePolling();
        cleanupActiveTerminalDocKeyHandler();
        waitingInput = false;
        fetch('/interactive/start', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ code: code, previous_run_id: previousRunId }),
        })
            .then(function (r) {
                return r.json().then(function (body) {
                    return { ok: r.ok, body: body };
                });
            })
            .then(function (x) {
                var first = box.querySelector('.edu-console__sys');
                if (first) first.remove();
                if (!x.ok) {
                    handleInteractivePhase({ success: false, message: x.body.message || 'Ошибка сервера' });
                    return;
                }
                if (x.body.run_id) interactiveRunId = x.body.run_id;
                if (x.body.status === 'running') startInteractivePolling();
                handleInteractivePhase(x.body);
            })
            .catch(function () {
                showNotification('Сеть или сервер недоступны', 'error');
                toggleStopBtn(false);
                stopInteractivePolling();
                renderIdleConsole();
            });
    }

    function appendRunDetails(root, data) {
        var meta = el('div', 'run-console__meta');
        var parts = [];
        if (data.duration_ms != null && data.duration_ms !== undefined) {
            parts.push('Время: ' + data.duration_ms + ' мс');
        }
        if (data.timed_out) parts.push('таймаут');
        else if (data.exit_code != null && data.exit_code !== undefined) {
            parts.push('код выхода: ' + data.exit_code);
        }
        meta.textContent = parts.length ? parts.join(' · ') : '—';
        root.appendChild(meta);

        var outBlock = el('div', 'run-console__block run-console__block--stdout');
        outBlock.appendChild(el('p', 'run-console__block-title', 'Вывод'));
        var outPre = el('pre', 'run-console__pre');
        var so = data.stdout != null ? data.stdout : '';
        outPre.textContent = so.length ? so : '(пусто)';
        outBlock.appendChild(outPre);
        root.appendChild(outBlock);

        var errText = data.stderr != null && data.stderr.trim() ? data.stderr : '';
        var errBlock = el('div', 'run-console__block run-console__block--stderr');
        errBlock.appendChild(el('p', 'run-console__block-title', 'Сообщение об ошибке'));
        var errPre = el('pre', 'run-console__pre');
        errPre.textContent = errText || '(пусто)';
        errBlock.appendChild(errPre);
        root.appendChild(errBlock);
    }

    function renderCheckConsole(data, verdictClass, verdictText) {
        var box = getConsoleBox();
        if (!box) return;
        box.className = 'edu-console';
        clearRunConsole(box);

        var v = el('div', 'run-console__verdict ' + verdictClass);
        v.textContent = verdictText;
        box.appendChild(v);

        if (data.already_completed) {
            setConsoleStatus('done', '');
            return;
        }

        if (data.success === false && data.expected != null) {
            var expBlock = el('div', 'run-console__block run-console__block--expected');
            expBlock.appendChild(el('p', 'run-console__block-title', 'Ожидаемый вывод (эталон)'));
            var expPre = el('pre', 'run-console__pre');
            expPre.textContent = String(data.expected);
            expBlock.appendChild(expPre);
            box.appendChild(expBlock);
        }

        appendRunDetails(box, data);
        setConsoleStatus(data.success ? 'done' : 'err', '');
    }

    function checkCode() {
        if ((cfg.taskType || 'code') !== 'code') return;

        fetch('/check_code', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                code: getCodeValue(),
                task_id: cfg.currentTaskId,
                stdin: lastStdinForCheck || '',
            }),
        })
            .then(function (r) {
                return r.json();
            })
            .then(function (data) {
                if (data.error && !data.hasOwnProperty('success')) {
                    showNotification(data.error || 'Ошибка', 'error');
                    return;
                }
                if (data.success) {
                    if (data.already_completed) {
                        showNotification('Задание уже выполнено', 'info');
                        renderCheckConsole(
                            data,
                            'run-console__verdict--info',
                            'Задание уже было решено ранее.'
                        );
                    } else {
                        renderCheckConsole(
                            data,
                            'run-console__verdict--ok',
                            'Верно · +' + data.xp_gained + ' XP · всего ' + data.total_xp + ' XP'
                        );
                        showNotification('Отлично! +' + data.xp_gained + ' XP', 'success');
                        saveCodeToStorage();
                        fetchSession();
                        if (data.project_code_saved) {
                            saveProjectCodeToStorage(getCodeValue());
                        }
                        if (data.project_meta) {
                            applyProjectMeta(data.project_meta);
                        }
                        markCurrentTopicTaskDone(cfg.currentTaskId);
                        if (data.module_completed) {
                            showNotification('Модуль завершён', 'success');
                            setTimeout(function () {
                                if (confirm('Перейти к следующему заданию?')) nextTask();
                            }, 600);
                        } else {
                            var btn = document.getElementById('checkCodeBtn');
                            if (btn) {
                                var orig = btn.textContent;
                                btn.disabled = true;
                                btn.style.opacity = '0.65';
                                btn.textContent = 'Готово';
                                setTimeout(function () {
                                    btn.disabled = false;
                                    btn.style.opacity = '1';
                                    btn.textContent = orig;
                                }, 1600);
                            }
                        }
                    }
                } else {
                    var wrong =
                        'Пока не совпало с эталоном · сравните вывод ниже и попробуйте снова.';
                    if (data.test_failures && data.test_failures.length) {
                        wrong = data.test_failures.join(' · ');
                    }
                    renderCheckConsole(data, 'run-console__verdict--fail', wrong);
                    showNotification('Попробуйте ещё раз', 'error');
                    saveCodeToStorage();
                }
            })
            .catch(function () {
                showNotification('Сеть или сервер недоступны', 'error');
            });
    }

    function collectInteractiveAnswer(safe) {
        var t = safe.type;
        if (t === 'quiz') {
            var q = document.querySelector('input[name="quiz-opt"]:checked');
            return q ? q.value : null;
        }
        if (t === 'ordering') {
            var lis = document.querySelectorAll('.ordering-list__text');
            var out = [];
            for (var i = 0; i < lis.length; i++) out.push(lis[i].textContent);
            return out;
        }
        if (t === 'matching') {
            var sel = document.querySelectorAll('.matching-select');
            var pairs = [];
            for (var j = 0; j < sel.length; j++) pairs.push(parseInt(sel[j].value, 10));
            return pairs;
        }
        if (t === 'fill_gaps') {
            var ins = document.querySelectorAll('.fill-gap-input');
            var ans = [];
            for (var k = 0; k < ins.length; k++) ans.push(ins[k].value || '');
            return ans;
        }
        return null;
    }

    function cleanupOrderingDragArtifacts() {
        document.body.classList.remove('ordering-drag-active');
        var stuck = document.querySelectorAll('body > .ordering-list__item');
        for (var i = 0; i < stuck.length; i++) stuck[i].remove();
    }

    function setupOrderingListDrag(list) {
        if (!list) return;
        cleanupOrderingDragArtifacts();

        var drag = null;

        function getItems() {
            return Array.prototype.slice.call(list.querySelectorAll('.ordering-list__item'));
        }

        function clearDropMarks() {
            var rows = list.querySelectorAll(
                '.ordering-list__item--drop-before, .ordering-list__item--drop-after'
            );
            for (var i = 0; i < rows.length; i++) {
                rows[i].classList.remove(
                    'ordering-list__item--drop-before',
                    'ordering-list__item--drop-after'
                );
            }
        }

        function insertIndexForY(y, dragged) {
            var items = getItems();
            for (var i = 0; i < items.length; i++) {
                if (items[i] === dragged) continue;
                var rect = items[i].getBoundingClientRect();
                if (y < rect.top + rect.height / 2) return i;
            }
            return items.length;
        }

        function moveItemToIndex(item, insertIndex) {
            var items = getItems();
            var cur = items.indexOf(item);
            if (cur < 0) return;
            if (insertIndex === cur || insertIndex === cur + 1) return;
            var ref = insertIndex >= items.length ? null : items[insertIndex];
            list.insertBefore(item, ref);
        }

        function showDropMark(insertIndex) {
            clearDropMarks();
            var items = getItems();
            if (!items.length) return;
            if (insertIndex >= items.length) {
                items[items.length - 1].classList.add('ordering-list__item--drop-after');
                return;
            }
            if (items[insertIndex]) items[insertIndex].classList.add('ordering-list__item--drop-before');
        }

        function endDrag() {
            if (!drag) return;
            drag.item.classList.remove('ordering-list__item--dragging');
            clearDropMarks();
            document.body.classList.remove('ordering-drag-active');
            document.removeEventListener('pointermove', onPointerMove);
            document.removeEventListener('pointerup', onPointerUp);
            document.removeEventListener('pointercancel', onPointerUp);
            try {
                if (drag.handle && drag.handle.releasePointerCapture) {
                    drag.handle.releasePointerCapture(drag.pointerId);
                }
            } catch (err) {}
            drag = null;
        }

        function onPointerMove(e) {
            if (!drag || e.pointerId !== drag.pointerId) return;

            if (!drag.active) {
                if (Math.abs(e.clientY - drag.startY) < 8) return;
                drag.active = true;
                drag.item.classList.add('ordering-list__item--dragging');
                document.body.classList.add('ordering-drag-active');
            }

            e.preventDefault();
            var idx = insertIndexForY(e.clientY, drag.item);
            if (idx !== drag.lastIndex) {
                moveItemToIndex(drag.item, idx);
                drag.lastIndex = idx;
            }
            showDropMark(idx);
        }

        function onPointerUp(e) {
            if (!drag || e.pointerId !== drag.pointerId) return;
            endDrag();
        }

        function bindMoveButtons() {
            var upBtns = list.querySelectorAll('[data-order-up]');
            for (var u = 0; u < upBtns.length; u++) {
                upBtns[u].addEventListener('click', function (e) {
                    e.preventDefault();
                    var row = e.currentTarget.closest('.ordering-list__item');
                    if (!row) return;
                    var prev = row.previousElementSibling;
                    if (prev) list.insertBefore(row, prev);
                });
            }
            var downBtns = list.querySelectorAll('[data-order-down]');
            for (var d = 0; d < downBtns.length; d++) {
                downBtns[d].addEventListener('click', function (e) {
                    e.preventDefault();
                    var row = e.currentTarget.closest('.ordering-list__item');
                    if (!row) return;
                    var next = row.nextElementSibling;
                    if (next) list.insertBefore(next, row);
                });
            }
        }

        var handles = list.querySelectorAll('.ordering-list__handle');
        for (var h = 0; h < handles.length; h++) {
            (function (handle) {
                handle.addEventListener('pointerdown', function (e) {
                    if (e.pointerType === 'mouse' && e.button !== 0) return;
                    if (drag) return;
                    var item = handle.closest('.ordering-list__item');
                    if (!item || !list.contains(item)) return;

                    e.preventDefault();
                    drag = {
                        item: item,
                        handle: handle,
                        pointerId: e.pointerId,
                        startY: e.clientY,
                        lastIndex: getItems().indexOf(item),
                        active: false,
                    };

                    try {
                        handle.setPointerCapture(e.pointerId);
                    } catch (err) {}

                    document.addEventListener('pointermove', onPointerMove, { passive: false });
                    document.addEventListener('pointerup', onPointerUp);
                    document.addEventListener('pointercancel', onPointerUp);
                });
            })(handles[h]);
        }

        bindMoveButtons();
    }

    function mountInteractiveTask() {
        var mount = document.getElementById('interactiveTaskMount');
        if (!mount || !cfg.safeTask) return;
        mount.innerHTML = '';
        var safe = cfg.safeTask;
        if ((cfg.taskType || 'code') === 'code') return;

        var wrap = el('div', 'interactive-task');

        if (cfg.taskDone) {
            var done = el('div', 'interactive-task__done');
            done.textContent = 'Задание выполнено · +' + cfg.taskXpEarned + ' XP';
            wrap.appendChild(done);
            mount.appendChild(wrap);
            return;
        }

        var body = el('div', 'interactive-task__body');

        if (safe.type === 'quiz') {
            var form = el('div', 'quiz-block');
            for (var i = 0; i < safe.options.length; i++) {
                var o = safe.options[i];
                var lab = document.createElement('label');
                lab.className = 'quiz-option';
                var inp = document.createElement('input');
                inp.type = 'radio';
                inp.name = 'quiz-opt';
                inp.value = o.key;
                lab.appendChild(inp);
                lab.appendChild(document.createTextNode(' ' + o.label));
                form.appendChild(lab);
            }
            body.appendChild(form);
        } else if (safe.type === 'ordering') {
            var ol = el('ol', 'ordering-list');
            for (var j = 0; j < safe.items.length; j++) {
                var li = el('li', 'ordering-list__item');
                var handle = el('span', 'ordering-list__handle');
                handle.setAttribute('role', 'button');
                handle.setAttribute('aria-label', 'Перетащите для смены порядка');
                handle.title = 'Перетащите для смены порядка';
                var txt = el('span', 'ordering-list__text', safe.items[j]);
                var up = el('button', 'btn btn-ghost ordering-btn', '↑');
                up.type = 'button';
                up.setAttribute('data-order-up', '1');
                up.setAttribute('aria-label', 'Выше');
                var dn = el('button', 'btn btn-ghost ordering-btn', '↓');
                dn.type = 'button';
                dn.setAttribute('data-order-down', '1');
                dn.setAttribute('aria-label', 'Ниже');
                li.appendChild(handle);
                li.appendChild(txt);
                li.appendChild(up);
                li.appendChild(dn);
                ol.appendChild(li);
            }
            setupOrderingListDrag(ol);
            body.appendChild(ol);
            body.appendChild(
                el(
                    'p',
                    'interactive-task__hint',
                    'Перетащите за ручку слева или нажимайте ↑ ↓. Сверху — самый первый шаг.'
                )
            );
        } else if (safe.type === 'matching') {
            var tbl = el('div', 'matching-grid');
            for (var k = 0; k < safe.left.length; k++) {
                var row = el('div', 'matching-row');
                row.appendChild(el('span', 'matching-left', safe.left[k]));
                var sel = document.createElement('select');
                sel.className = 'matching-select';
                sel.setAttribute('aria-label', 'Сопоставление для строки ' + (k + 1));
                for (var r = 0; r < safe.right.length; r++) {
                    var opt = document.createElement('option');
                    opt.value = String(r);
                    opt.textContent = safe.right[r];
                    sel.appendChild(opt);
                }
                row.appendChild(sel);
                tbl.appendChild(row);
            }
            body.appendChild(tbl);
        } else if (safe.type === 'fill_gaps') {
            if (safe.template) {
                var tp = el('p', 'fill-gaps__template', safe.template);
                body.appendChild(tp);
            }
            var n = safe.blank_count || 0;
            var gapsWrap = el('div', 'fill-gaps');
            for (var g = 0; g < n; g++) {
                var rowg = el('div', 'fill-gaps__row');
                rowg.appendChild(el('span', 'fill-gaps__label', 'Пропуск ' + (g + 1)));
                var inp = document.createElement('input');
                inp.type = 'text';
                inp.className = 'fill-gap-input';
                inp.autocomplete = 'off';
                rowg.appendChild(inp);
                gapsWrap.appendChild(rowg);
            }
            body.appendChild(gapsWrap);
        }

        var actions = el('div', 'interactive-task__actions');
        var chk = el('button', 'btn btn-accent', 'Проверить');
        chk.type = 'button';
        chk.id = 'checkInteractiveBtn';
        actions.appendChild(chk);
        wrap.appendChild(body);
        wrap.appendChild(actions);
        mount.appendChild(wrap);

        chk.addEventListener('click', function () {
            var ans = collectInteractiveAnswer(safe);
            if (ans === null || (safe.type === 'quiz' && ans === null)) {
                showNotification('Выберите или заполните ответ', 'info');
                return;
            }
            fetch('/check_task', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ task_id: cfg.currentTaskId, answer: ans }),
            })
                .then(function (r) {
                    return r.json();
                })
                .then(function (data) {
                    if (data.error && !data.hasOwnProperty('success')) {
                        showNotification(data.error || 'Ошибка', 'error');
                        return;
                    }
                    if (data.success) {
                        if (data.already_completed) {
                            showNotification('Задание уже выполнено', 'info');
                            return;
                        }
                        showNotification('Отлично! +' + data.xp_gained + ' XP', 'success');
                        fetchSession();
                        applyLevelUi(data.level);
                        if (data.project_meta) applyProjectMeta(data.project_meta);
                        markCurrentTopicTaskDone(cfg.currentTaskId);
                        var xpSide = document.querySelector('[data-total-xp]');
                        if (xpSide) xpSide.textContent = String(data.total_xp);
                        setTimeout(function () {
                            refreshLearnTaskInPlace().catch(function () {
                                location.reload();
                            });
                        }, 700);
                    } else {
                        showNotification(data.message || 'Попробуйте ещё раз', 'error');
                    }
                })
                .catch(function () {
                    showNotification('Сеть недоступна', 'error');
                });
        });
    }

    function nextTask() {
        saveCodeToStorage();
        fetch('/next_task', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                module_num: cfg.currentModule,
                task_index: cfg.currentTaskIndex,
            }),
        })
            .then(function (r) {
                return r.json();
            })
            .then(function (data) {
                if (data.completed) {
                    showNotification('Все задания пройдены!', 'success');
                    setTimeout(function () {
                        location.reload();
                    }, 1200);
                } else {
                    handleTaskNavResponse(data);
                }
            });
    }

    function previousTask() {
        saveCodeToStorage();
        fetch('/previous_task', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                module_num: cfg.currentModule,
                task_index: cfg.currentTaskIndex,
            }),
        })
            .then(function (r) {
                return r.json();
            })
            .then(function (data) {
                handleTaskNavResponse(data);
            });
    }

    function loadModule(moduleId) {
        saveCodeToStorage();
        if (moduleId !== cfg.currentModule) {
            markLearnScrollToTop();
        }
        window.location.href = '/load_module/' + moduleId;
    }

    function resetProgress() {
        if (!confirm('Сбросить весь прогресс?')) return;
        localStorage.clear();
        fetch('/reset_progress', { method: 'POST' }).then(function () {
            markLearnScrollToTop();
            location.reload();
        });
    }

    function confirmClearEditor() {
        if (cfg.isProjectStage) {
            return window.confirm(
                'Очистить редактор проекта?\n\n' +
                    'Код main.py будет сброшен до шаблона. Сохранённый код проекта ' +
                    'исчезнет — в следующих темах его не подставят автоматически.\n\n' +
                    'Нажмите «ОК», только если вы уверены.'
            );
        }
        return window.confirm(
            'Очистить редактор?\n\n' +
                'Текущий код в этом задании будет удалён.\n' +
                'Если передумали — нажмите «Отмена».'
        );
    }

    function bindClearEditorButton() {
        var clearBtn = document.getElementById('clearCodeBtn');
        if (!clearBtn) return;
        var btn = clearBtn.cloneNode(true);
        clearBtn.parentNode.replaceChild(btn, clearBtn);
        btn.addEventListener('click', function (e) {
            e.preventDefault();
            if (!confirmClearEditor()) return;
            clearCode();
        });
    }

    function clearCode() {
        clearTimeout(saveDebounceTimer);
        abortInteractive(true);
        localStorage.removeItem(codeStorageKey());
        var resetTo = cfg.editorTemplate;
        if (cfg.isProjectStage) {
            localStorage.removeItem(projectCodeStorageKey());
            resetTo = cfg.editorStarter || cfg.editorTemplate;
        }
        setCodeValue(resetTo, true);
        saveCodeToStorage();
        if (cfg.isProjectStage) {
            saveProjectCodeToStorage(resetTo);
        }
        lastStdinForCheck = '';
        renderIdleConsole();
        armPlaceholderStripOnce();
        showNotification('Редактор очищен', 'info');
    }

    function normalizePlaceholderText(s) {
        return String(s || '')
            .replace(/\r\n/g, '\n')
            .replace(/\s+$/, '');
    }

    /** Пустой старт задания: новый плейсхолдер или старый с «...» */
    function isPlaceholderContent(text) {
        var t = normalizePlaceholderText(text);
        return t === '# Напишите код здесь. . .' || t === '# Напишите код здесь...';
    }

    /** Один раз при первом клике по редактору или консоли убрать шаблон-подсказку. */
    function armPlaceholderStripOnce() {
        if (!isPlaceholderContent(cfg.editorTemplate)) return;
        if (!isPlaceholderContent(getCodeValue())) return;

        var stripDone = false;
        function tryStripPlaceholderOnce() {
            if (stripDone) return;
            if (!isPlaceholderContent(getCodeValue())) return;
            stripDone = true;
            setCodeValue('', false);
            scheduleSaveCode();
        }

        var runConsole = document.getElementById('runConsole');
        var workbenchBody = document.querySelector('.code-workbench__body');
        if (workbenchBody) {
            workbenchBody.addEventListener('pointerdown', tryStripPlaceholderOnce, { capture: true, once: true });
        }
        if (runConsole) {
            runConsole.addEventListener('pointerdown', tryStripPlaceholderOnce, { capture: true, once: true });
        }
    }

    function setupCodeEditor() {
        var mount = document.getElementById('codeEditorMount');
        if (!mount || !window.LearnCodeEditor || !window.LearnCodeEditor.create) return;

        window.LearnCodeEditor.destroy();
        var saved = localStorage.getItem(codeStorageKey());
        var projectSaved = getProjectCodeFromStorage();
        var initial = cfg.editorTemplate;
        if (cfg.isProjectStage) {
            if (projectSaved !== null && projectSaved !== '') {
                initial = projectSaved;
            } else if (cfg.projectCodeServer) {
                initial = cfg.projectCodeServer;
            }
        } else if (saved !== null && saved !== '') {
            initial = saved;
        }

        window.LearnCodeEditor.create(mount, {
            initial: initial,
            onChange: scheduleSaveCode,
        });

        armPlaceholderStripOnce();
    }

    function bindLearnTaskUi() {
        var tt = cfg.taskType || 'code';

        if (tt === 'code') {
            bindClearEditorButton();
        }

        var hintBtn = document.getElementById('hintBtn');
        if (hintBtn) {
            hintBtn.addEventListener('click', function () {
                showNotification('Подсказка: ' + cfg.hint, 'info');
            });
        }

        var prevBtn = document.getElementById('prevTaskBtn');
        if (prevBtn) {
            prevBtn.addEventListener('click', function (e) {
                e.preventDefault();
                previousTask();
            });
        }
        var nextNav = document.getElementById('nextTaskNavBtn');
        if (nextNav) {
            nextNav.addEventListener('click', function (e) {
                e.preventDefault();
                nextTask();
            });
        }

        if (tt !== 'code') {
            mountInteractiveTask();
            return;
        }

        var mount = document.getElementById('codeEditorMount');
        if (!mount) return;

        ensureCodeEditorReady().then(function () {
            setupCodeEditor();
        });

        var runBtn = document.getElementById('runCodeBtn');
        if (runBtn) {
            runBtn.addEventListener('click', function (e) {
                e.preventDefault();
                runInteractiveExecute();
            });
        }
        var stopBtn = document.getElementById('stopRunBtn');
        if (stopBtn) {
            stopBtn.addEventListener('click', function (e) {
                e.preventDefault();
                abortInteractive(false);
            });
        }
        var checkBtn = document.getElementById('checkCodeBtn');
        if (checkBtn) {
            checkBtn.addEventListener('click', function (e) {
                e.preventDefault();
                checkCode();
            });
        }

        if (cfg.taskDone) {
            var box = getConsoleBox();
            if (box) {
                box.className = 'edu-console';
                clearRunConsole(box);
                var v = el('div', 'run-console__verdict run-console__verdict--ok');
                v.textContent = 'Задание выполнено · +' + cfg.taskXpEarned + ' XP';
                box.appendChild(v);
                setConsoleStatus('done', '');
            }
        } else {
            renderIdleConsole();
        }
    }

    function init() {
        initSidebarModules();
        initSidebarsScrollMemory();
        initLearnNavigationScroll();
        initReadingModeToggle();
        initPanelVisibilityToggle();

        var elCfg = document.getElementById('learn-config');
        if (!elCfg) return;
        try {
            cfg = JSON.parse(elCfg.textContent);
        } catch (e) {
            return;
        }

        if (cfg.projectMeta) applyProjectMeta(cfg.projectMeta);

        window.nextTask = nextTask;
        window.previousTask = previousTask;
        window.loadModule = loadModule;
        window.resetProgress = resetProgress;

        bindLearnTaskUi();
        bindTopicTaskNav();
        bindSchemeLightbox();
        initCourseGradeDemoControls();
        updateTopicTaskNav();

        if (!window._learnPageHooksBound) {
            window._learnPageHooksBound = true;
            window.addEventListener('beforeunload', function () {
                clearTimeout(saveDebounceTimer);
                saveCodeToStorage();
            });
        }
    }

    document.addEventListener('DOMContentLoaded', init);
})();
