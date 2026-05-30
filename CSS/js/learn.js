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

    function markLearnScrollToTop() {
        try {
            sessionStorage.setItem(LEARN_SCROLL_KEY, '1');
        } catch (e) {}
    }

    function scrollLearnPageToTopSmooth() {
        try {
            window.scrollTo({ top: 0, behavior: 'smooth' });
        } catch (e) {
            window.scrollTo(0, 0);
        }
    }

    function applyLearnScrollOnLoad() {
        try {
            if (sessionStorage.getItem(LEARN_SCROLL_KEY)) {
                sessionStorage.removeItem(LEARN_SCROLL_KEY);
                if ('scrollRestoration' in history) history.scrollRestoration = 'manual';
                scrollLearnPageToTopSmooth();
            }
        } catch (e) {}
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
                }
                bindLearnTaskUi();
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

    function initLearnNavigationScroll() {
        applyLearnScrollOnLoad();

        document.querySelectorAll('.topic-sidebar-nav__link[href]').forEach(function (link) {
            link.addEventListener('click', function () {
                if (!link.classList.contains('topic-sidebar-nav__link--active')) {
                    markLearnScrollToTop();
                }
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

    function applySessionPayload(d) {
        if (!d || !d.success) return;
        var xpSide = document.querySelector('[data-total-xp]');
        if (xpSide) xpSide.textContent = String(d.total_xp);
        var doneEl = document.querySelector('[data-completed-count]');
        if (doneEl) doneEl.textContent = d.completed_tasks + ' / ' + d.total_tasks;
        var pp = document.querySelector('.sidebar-left .progress-card__percent');
        var pf = document.querySelector('.sidebar-left .sidebar-main-progress .duo-progress__fill');
        if (pp) pp.textContent = d.module_progress + '%';
        if (pf) pf.style.width = d.module_progress + '%';
        if (d.level) applyLevelUi(d.level);
        var items = document.querySelectorAll('.module-row[data-module-id]');
        for (var i = 0; i < items.length; i++) {
            var mid = parseInt(items[i].getAttribute('data-module-id'), 10);
            if (mid === d.current_module) {
                var sp = items[i].querySelector('.module-progress span');
                var bar = items[i].querySelector('.duo-progress__fill');
                if (sp) sp.textContent = d.module_progress + '%';
                if (bar) bar.style.width = d.module_progress + '%';
            }
        }
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
                var txt = el('span', 'ordering-list__text', safe.items[j]);
                var up = el('button', 'btn btn-ghost ordering-btn', '↑');
                up.type = 'button';
                var dn = el('button', 'btn btn-ghost ordering-btn', '↓');
                dn.type = 'button';
                li.appendChild(txt);
                li.appendChild(up);
                li.appendChild(dn);
                ol.appendChild(li);
                up.addEventListener(
                    'click',
                    function (row) {
                        return function () {
                            var prev = row.previousElementSibling;
                            if (prev) ol.insertBefore(row, prev);
                        };
                    }(li)
                );
                dn.addEventListener(
                    'click',
                    function (row) {
                        return function () {
                            var nx = row.nextElementSibling;
                            if (nx) ol.insertBefore(nx, row);
                        };
                    }(li)
                );
            }
            body.appendChild(ol);
            body.appendChild(el('p', 'interactive-task__hint', 'Расставьте шаги кнопками ↑ ↓'));
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
                        var xpSide = document.querySelector('[data-total-xp]');
                        if (xpSide) xpSide.textContent = String(data.total_xp);
                        setTimeout(function () {
                            location.reload();
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

    function clearCode() {
        clearTimeout(saveDebounceTimer);
        abortInteractive(true);
        localStorage.removeItem(codeStorageKey());
        setCodeValue(cfg.editorTemplate, true);
        lastStdinForCheck = '';
        renderIdleConsole();
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

    function setupCodeEditor() {
        var mount = document.getElementById('codeEditorMount');
        if (!mount || !window.LearnCodeEditor || !window.LearnCodeEditor.create) return;

        window.LearnCodeEditor.destroy();
        var saved = localStorage.getItem(codeStorageKey());
        var initial = saved !== null && saved !== '' ? saved : cfg.editorTemplate;
        var shouldArmPlaceholderStrip =
            isPlaceholderContent(cfg.editorTemplate) && isPlaceholderContent(initial);

        window.LearnCodeEditor.create(mount, {
            initial: initial,
            onChange: scheduleSaveCode,
        });

        if (!shouldArmPlaceholderStrip) return;

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

    function bindLearnTaskUi() {
        var tt = cfg.taskType || 'code';

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
        var clearBtn = document.getElementById('clearCodeBtn');
        if (clearBtn) {
            clearBtn.addEventListener('click', function (e) {
                e.preventDefault();
                if (
                    !window.confirm(
                        'Очистить редактор? Текущий код в этом задании будет удалён. Если вы передумали, нажмите «Отмена».'
                    )
                ) {
                    return;
                }
                clearCode();
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
        var elCfg = document.getElementById('learn-config');
        if (!elCfg) return;
        try {
            cfg = JSON.parse(elCfg.textContent);
        } catch (e) {
            return;
        }

        initLearnNavigationScroll();

        window.nextTask = nextTask;
        window.previousTask = previousTask;
        window.loadModule = loadModule;
        window.resetProgress = resetProgress;

        bindLearnTaskUi();

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
