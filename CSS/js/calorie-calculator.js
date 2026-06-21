(function () {
    'use strict';

    var SLIDER_MAX = 1000;
    var DEFAULT_GRAMS = 100;
    var openPicker = null;
    var sortedProductsCache = null;

    var GROUP_ORDER = [
        'Крупы и макароны',
        'Хлеб и выпечка',
        'Овощи',
        'Фрукты и ягоды',
        'Мясо и птица',
        'Колбасы и сосиски',
        'Рыба и морепродукты',
        'Яйца',
        'Молочные продукты',
        'Бобовые',
        'Масла и соусы',
        'Напитки',
        'Сладости',
        'Орехи и семена',
        'Прочее',
        'Деликатесы и редкое',
    ];

    function readProducts() {
        var el = document.getElementById('dish-calc-products');
        if (!el) return [];
        try {
            return JSON.parse(el.textContent || '[]');
        } catch (e) {
            return [];
        }
    }

    function readRecipes() {
        var el = document.getElementById('dish-calc-recipes');
        if (!el) return [];
        try {
            return JSON.parse(el.textContent || '[]');
        } catch (e) {
            return [];
        }
    }

    function getRecipeById(recipes, id) {
        for (var i = 0; i < recipes.length; i++) {
            if (recipes[i].id === id) return recipes[i];
        }
        return null;
    }

    function formatKcal(value) {
        var n = Number(value);
        if (!isFinite(n)) return '0';
        if (Math.abs(n - Math.round(n)) < 0.05) return String(Math.round(n));
        return n.toFixed(1);
    }

    function formatWeight(value) {
        var n = Number(value);
        if (!isFinite(n)) return '0';
        return String(Math.round(n));
    }

    function calcRowKcal(kcalPer100, grams) {
        return (Number(kcalPer100) * Number(grams)) / 100;
    }

    function escapeHtml(text) {
        return String(text)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;');
    }

    function normalizeQuery(text) {
        return String(text).toLowerCase().replace(/ё/g, 'е').trim();
    }

    function groupSortIndex(group) {
        var idx = GROUP_ORDER.indexOf(group || 'Прочее');
        return idx === -1 ? GROUP_ORDER.length : idx;
    }

    function getSortedProducts(products) {
        if (sortedProductsCache && sortedProductsCache._source === products) {
            return sortedProductsCache.list;
        }
        var list = products.slice().sort(function (a, b) {
            var ga = groupSortIndex(a.group);
            var gb = groupSortIndex(b.group);
            if (ga !== gb) return ga - gb;
            return a.name.localeCompare(b.name, 'ru');
        });
        sortedProductsCache = { _source: products, list: list };
        return list;
    }

    function filterProducts(products, query) {
        var sorted = getSortedProducts(products);
        var q = normalizeQuery(query);
        if (!q) return sorted;
        return sorted.filter(function (p) {
            var name = normalizeQuery(p.name);
            var group = normalizeQuery(p.group || '');
            return name.indexOf(q) !== -1 || group.indexOf(q) !== -1;
        });
    }

    function getProductById(products, id) {
        for (var i = 0; i < products.length; i++) {
            if (products[i].id === id) return products[i];
        }
        return null;
    }

    function closePicker(picker) {
        if (!picker) return;
        var list = picker.querySelector('[data-field="product-list"]');
        var search = picker.querySelector('[data-field="product-search"]');
        var toggle = picker.querySelector('[data-field="product-toggle"]');
        if (list) list.hidden = true;
        if (search) search.setAttribute('aria-expanded', 'false');
        if (toggle) toggle.setAttribute('aria-expanded', 'false');
        picker.classList.remove('dish-calc-product-picker--open');
        if (openPicker === picker) openPicker = null;
    }

    function renderProductList(picker, products, query) {
        var list = picker.querySelector('[data-field="product-list"]');
        var matched = filterProducts(products, query);
        var q = normalizeQuery(query);
        var html = '';

        if (!matched.length) {
            list.innerHTML = '<li class="dish-calc-product-list__empty">Ничего не найдено</li>';
            list.hidden = false;
            return;
        }

        if (!q) {
            html += '<li class="dish-calc-product-list__hint">'
                + products.length + ' продуктов — прокрутите список или начните ввод для поиска</li>';
        } else {
            html += '<li class="dish-calc-product-list__hint">Найдено: ' + matched.length + '</li>';
        }

        var lastGroup = null;
        matched.forEach(function (p) {
            var group = p.group || 'Прочее';
            if (group !== lastGroup) {
                lastGroup = group;
                html += '<li class="dish-calc-product-group" aria-hidden="true">' + escapeHtml(group) + '</li>';
            }
            html += '<li class="dish-calc-product-option" role="option" data-product-id="'
                + escapeHtml(p.id) + '" tabindex="-1">'
                + '<span class="dish-calc-product-option__name">' + escapeHtml(p.name) + '</span>'
                + '<span class="dish-calc-product-option__kcal">' + formatKcal(p.kcal) + ' ккал / 100 г</span>'
                + '</li>';
        });

        list.innerHTML = html;
        list.hidden = false;
    }

    function setProductSelection(picker, products, productId, refresh) {
        var hidden = picker.querySelector('[data-field="product"]');
        var search = picker.querySelector('[data-field="product-search"]');
        var product = productId ? getProductById(products, productId) : null;
        hidden.value = product ? product.id : '';
        search.value = product ? product.name : '';
        closePicker(picker);
        if (refresh) refresh();
    }

    function initProductPicker(picker, products, refresh) {
        var search = picker.querySelector('[data-field="product-search"]');
        var list = picker.querySelector('[data-field="product-list"]');
        var hidden = picker.querySelector('[data-field="product"]');
        var toggle = picker.querySelector('[data-field="product-toggle"]');

        function openList() {
            if (openPicker && openPicker !== picker) closePicker(openPicker);
            openPicker = picker;
            picker.classList.add('dish-calc-product-picker--open');
            renderProductList(picker, products, search.value);
            search.setAttribute('aria-expanded', 'true');
            if (toggle) toggle.setAttribute('aria-expanded', 'true');
        }

        function toggleList(e) {
            if (e) e.preventDefault();
            if (openPicker === picker && !list.hidden) {
                closePicker(picker);
                return;
            }
            openList();
            search.focus();
        }

        search.addEventListener('focus', openList);
        search.addEventListener('click', openList);
        search.addEventListener('input', function () {
            var selected = hidden.value ? getProductById(products, hidden.value) : null;
            if (!selected || normalizeQuery(search.value) !== normalizeQuery(selected.name)) {
                hidden.value = '';
            }
            openList();
            refresh();
        });
        search.addEventListener('keydown', function (e) {
            if (e.key === 'Escape') {
                closePicker(picker);
                search.blur();
            }
            if (e.key === 'ArrowDown' && list.hidden) {
                openList();
            }
        });

        if (toggle) {
            toggle.addEventListener('mousedown', function (e) {
                e.preventDefault();
            });
            toggle.addEventListener('click', toggleList);
        }

        list.addEventListener('mousedown', function (e) {
            var option = e.target.closest('.dish-calc-product-option');
            if (!option) return;
            e.preventDefault();
            setProductSelection(picker, products, option.getAttribute('data-product-id'), refresh);
        });

        picker._setProduct = function (productId) {
            setProductSelection(picker, products, productId, refresh);
        };
        picker._clearProduct = function () {
            hidden.value = '';
            search.value = '';
            closePicker(picker);
            refresh();
        };
    }

    function createRow(products, state) {
        state = state || {};
        var row = document.createElement('div');
        row.className = 'dish-calc-row';
        row.innerHTML =
            '<div class="dish-calc-row__product">'
            + '<label class="dish-calc-label dish-calc-label--sr">Продукт</label>'
            + '<div class="dish-calc-product-picker" data-field="product-picker">'
            + '<div class="dish-calc-product-combo">'
            + '<input type="text" class="dish-calc-product-search" data-field="product-search"'
            + ' placeholder="Выберите из списка или введите название…" autocomplete="off" role="combobox"'
            + ' aria-expanded="false" aria-autocomplete="list">'
            + '<button type="button" class="dish-calc-product-toggle" data-field="product-toggle"'
            + ' aria-label="Открыть список продуктов" aria-expanded="false" tabindex="-1"></button>'
            + '</div>'
            + '<input type="hidden" data-field="product" value="">'
            + '<ul class="dish-calc-product-list" data-field="product-list" role="listbox" hidden></ul>'
            + '</div>'
            + '</div>'
            + '<div class="dish-calc-row__weight">'
            + '<label class="dish-calc-label dish-calc-label--sr">Граммы</label>'
            + '<div class="dish-calc-weight-control">'
            + '<input type="number" class="dish-calc-weight-input" data-field="grams" min="0" max="5000" step="1" value="'
            + (state.grams != null ? state.grams : DEFAULT_GRAMS) + '">'
            + '<span class="dish-calc-weight-unit">грамм</span>'
            + '</div>'
            + '<input type="range" class="dish-calc-slider" data-field="slider" min="0" max="' + SLIDER_MAX
            + '" step="1" value="' + (state.grams != null ? state.grams : DEFAULT_GRAMS) + '">'
            + '</div>'
            + '<div class="dish-calc-row__result">'
            + '<span class="dish-calc-row-kcal" data-field="kcal">0</span>'
            + '<span class="dish-calc-row-kcal-unit">ккал</span>'
            + '</div>'
            + '<button type="button" class="dish-calc-row-remove" data-action="remove" aria-label="Удалить ингредиент" title="Удалить">×</button>';

        var productId = state.productId || state.product_id || '';
        if (productId) {
            var product = getProductById(products, productId);
            if (product) {
                row.querySelector('[data-field="product"]').value = product.id;
                row.querySelector('[data-field="product-search"]').value = product.name;
            }
        }

        return row;
    }

    function updateRow(row, products) {
        var hidden = row.querySelector('[data-field="product"]');
        var gramsInput = row.querySelector('[data-field="grams"]');
        var slider = row.querySelector('[data-field="slider"]');
        var kcalEl = row.querySelector('[data-field="kcal"]');

        var productId = hidden.value;
        var grams = Math.max(0, Number(gramsInput.value) || 0);
        gramsInput.value = grams;
        slider.value = Math.min(SLIDER_MAX, grams);

        var product = getProductById(products, productId);
        var kcal = product ? calcRowKcal(product.kcal, grams) : 0;
        kcalEl.textContent = formatKcal(kcal);

        row.dataset.kcal = String(kcal);
        row.dataset.grams = String(grams);
        row.dataset.valid = product && grams > 0 ? '1' : '0';
    }

    function recalcSummary(container) {
        var rows = container.querySelectorAll('.dish-calc-row');
        var totalWeight = 0;
        var totalKcal = 0;

        rows.forEach(function (row) {
            if (row.dataset.valid !== '1') return;
            totalWeight += Number(row.dataset.grams) || 0;
            totalKcal += Number(row.dataset.kcal) || 0;
        });

        var kcalPer100 = totalWeight > 0 ? (totalKcal / totalWeight) * 100 : 0;

        document.getElementById('dishTotalWeight').textContent = formatWeight(totalWeight);
        document.getElementById('dishTotalKcal').textContent = formatKcal(totalKcal);
        document.getElementById('dishKcalPer100').textContent = formatKcal(kcalPer100);
    }

    function bindRow(row, products, container) {
        var picker = row.querySelector('[data-field="product-picker"]');
        var gramsInput = row.querySelector('[data-field="grams"]');
        var slider = row.querySelector('[data-field="slider"]');
        var removeBtn = row.querySelector('[data-action="remove"]');

        function refresh() {
            updateRow(row, products);
            recalcSummary(container);
        }

        initProductPicker(picker, products, refresh);

        gramsInput.addEventListener('input', function () {
            slider.value = Math.min(SLIDER_MAX, Math.max(0, Number(gramsInput.value) || 0));
            refresh();
        });
        slider.addEventListener('input', function () {
            gramsInput.value = slider.value;
            refresh();
        });
        removeBtn.addEventListener('click', function () {
            if (container.querySelectorAll('.dish-calc-row').length <= 1) {
                picker._clearProduct();
                gramsInput.value = 0;
                slider.value = 0;
                refresh();
                return;
            }
            row.remove();
            recalcSummary(container);
        });

        refresh();
    }

    function setRows(container, products, rowStates) {
        container.innerHTML = '';
        if (!rowStates.length) {
            rowStates = [{ productId: '', grams: 0 }];
        }
        rowStates.forEach(function (state) {
            var row = createRow(products, {
                productId: state.productId || state.product_id || '',
                grams: state.grams != null ? state.grams : DEFAULT_GRAMS,
            });
            container.appendChild(row);
            bindRow(row, products, container);
        });
        recalcSummary(container);
    }

    function applyRecipe(recipe, products, container, dishNameInput) {
        if (!recipe) return;
        if (dishNameInput) dishNameInput.value = recipe.name;
        var ingredients = recipe.ingredients || [];
        var rowStates = ingredients.map(function (item) {
            return { productId: item.product_id, grams: item.grams };
        });
        setRows(container, products, rowStates);
        var firstGrams = container.querySelector('[data-field="grams"]');
        if (firstGrams) firstGrams.focus();
    }

    function init() {
        var products = readProducts();
        var recipes = readRecipes();
        var container = document.getElementById('dishCalcRows');
        var addBtn = document.getElementById('dishCalcAddBtn');
        var recipeSelect = document.getElementById('dishRecipe');
        var dishNameInput = document.getElementById('dishName');
        if (!container || !products.length) return;

        document.addEventListener('click', function (e) {
            if (!openPicker) return;
            if (openPicker.contains(e.target)) return;
            closePicker(openPicker);
        });

        setRows(container, products, [{ productId: '', grams: 0 }]);

        if (recipeSelect) {
            recipeSelect.addEventListener('change', function () {
                var recipeId = recipeSelect.value;
                if (!recipeId) {
                    if (dishNameInput) dishNameInput.value = '';
                    setRows(container, products, [{ productId: '', grams: 0 }]);
                    return;
                }
                var recipe = getRecipeById(recipes, recipeId);
                if (recipe) applyRecipe(recipe, products, container, dishNameInput);
            });
        }

        addBtn.addEventListener('click', function () {
            var row = createRow(products, { grams: DEFAULT_GRAMS });
            container.appendChild(row);
            bindRow(row, products, container);
            row.querySelector('[data-field="product-search"]').focus();
        });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
