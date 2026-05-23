// ── State ─────────────────────────────────────────────────────
let currentDate = new Date();
let allFoods = [];
let activeCategory = '';
let selectedFood = null;
let selectedMeal = 'Breakfast';
const GOAL = 2000;

// ── Helpers ───────────────────────────────────────────────────
function $(id) { return document.getElementById(id); }
function isoDate(d) { return d.toISOString().split('T')[0]; }
function fmtDate(d) { return d.toLocaleDateString('en-PK', { weekday:'short', day:'numeric', month:'short' }); }

function showToast(msg) {
  var t = document.querySelector('.toast');
  if (!t) { t = document.createElement('div'); t.className = 'toast'; document.body.appendChild(t); }
  t.textContent = msg;
  t.classList.add('show');
  setTimeout(function() { t.classList.remove('show'); }, 2200);
}

// ── Modal ─────────────────────────────────────────────────────
function openModal(food) {
  selectedFood = food;
  $('modalEmoji').textContent = food.emoji;
  $('modalTitle').textContent = food.name;
  $('modalMeta').textContent  = food.calories + ' kcal per ' + food.unit;
  $('qtyInput').value = 1;
  document.querySelectorAll('.meal-pill').forEach(function(b) { b.classList.remove('active'); });
  document.querySelector('.meal-pill[data-meal="Breakfast"]').classList.add('active');
  selectedMeal = 'Breakfast';
  updatePreview();
  $('modalBackdrop').style.cssText = 'display:flex !important;';
}

function closeModal() {
  $('modalBackdrop').style.cssText = 'display:none !important;';
  selectedFood = null;
}

function updatePreview() {
  if (!selectedFood) return;
  var qty = parseFloat($('qtyInput').value) || 1;
  $('previewCal').textContent = Math.round(selectedFood.calories * qty);
  $('previewP').textContent   = (Math.round(selectedFood.protein  * qty * 10) / 10);
  $('previewC').textContent   = (Math.round(selectedFood.carbs    * qty * 10) / 10);
  $('previewF').textContent   = (Math.round(selectedFood.fat      * qty * 10) / 10);
}

// Wire up modal buttons
$('modalClose').onclick = function(e) { e.stopPropagation(); closeModal(); };
$('modalBackdrop').onclick = function(e) { if (e.target === $('modalBackdrop')) closeModal(); };
document.onkeydown = function(e) { if (e.key === 'Escape') closeModal(); };

$('qtyMinus').onclick = function() {
  var v = parseFloat($('qtyInput').value);
  if (v > 0.25) { $('qtyInput').value = Math.round((v - 0.25) * 4) / 4; updatePreview(); }
};
$('qtyPlus').onclick = function() {
  $('qtyInput').value = Math.round((parseFloat($('qtyInput').value) + 0.25) * 4) / 4;
  updatePreview();
};
$('qtyInput').oninput = updatePreview;

document.querySelectorAll('.meal-pill').forEach(function(btn) {
  btn.onclick = function() {
    document.querySelectorAll('.meal-pill').forEach(function(b) { b.classList.remove('active'); });
    btn.classList.add('active');
    selectedMeal = btn.dataset.meal;
  };
});

$('confirmAdd').onclick = async function() {
  if (!selectedFood) return;
  var qty = parseFloat($('qtyInput').value) || 1;
  await fetch('/api/log', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ food_id: selectedFood.id, quantity: qty, meal: selectedMeal, date: isoDate(currentDate) })
  });
  var name = selectedFood.name;
  var emoji = selectedFood.emoji;
  closeModal();
  loadLog();
  loadWeekly();
  showToast(emoji + ' ' + name + ' logged!');
};

// ── Date nav ──────────────────────────────────────────────────
function updateDateLabel() {
  var today = new Date(); today.setHours(0,0,0,0);
  var cur = new Date(currentDate); cur.setHours(0,0,0,0);
  var diff = Math.round((cur - today) / 86400000);
  var label = diff === 0 ? 'Today' : diff === -1 ? 'Yesterday' : fmtDate(currentDate);
  $('currentDate').textContent = label;
}

$('prevDay').onclick = function() { currentDate.setDate(currentDate.getDate() - 1); updateDateLabel(); loadLog(); loadWeekly(); };
$('nextDay').onclick = function() { currentDate.setDate(currentDate.getDate() + 1); updateDateLabel(); loadLog(); loadWeekly(); };

// ── Food log ──────────────────────────────────────────────────
async function loadLog() {
  var res = await fetch('/api/log?date=' + isoDate(currentDate));
  var data = await res.json();
  renderLog(data);
  renderRing(data.totals.calories);
  $('totalProtein').textContent = data.totals.protein + 'g';
  $('totalCarbs').textContent   = data.totals.carbs   + 'g';
  $('totalFat').textContent     = data.totals.fat     + 'g';
}

function renderRing(calories) {
  var pct = Math.min(calories / GOAL, 1);
  $('ringFill').style.strokeDashoffset = 502 - pct * 502;
  $('totalCal').textContent = calories;
  document.querySelector('.ring').classList.toggle('over', calories > GOAL);
}

function renderLog(data) {
  var meals = ['Sehri','Breakfast','Lunch','Dinner','Snack'];
  var byMeal = {};
  meals.forEach(function(m) { byMeal[m] = []; });
  data.entries.forEach(function(e) { if (!byMeal[e.meal]) byMeal[e.meal] = []; byMeal[e.meal].push(e); });

  var container = $('mealSections');
  container.innerHTML = '';
  var hasAny = false;

  meals.forEach(function(meal) {
    var entries = byMeal[meal];
    if (!entries.length) return;
    hasAny = true;
    var mealCal = entries.reduce(function(s,e) { return s + e.calories; }, 0);
    var sec = document.createElement('div');
    sec.className = 'meal-section';
    sec.innerHTML = '<div class="meal-section-header"><span>' + meal + '</span><span class="meal-cal-badge">' + mealCal + ' kcal</span></div>';
    entries.forEach(function(entry) {
      var row = document.createElement('div');
      row.className = 'log-entry';
      row.innerHTML =
        '<span class="log-emoji">' + entry.emoji + '</span>' +
        '<span class="log-name">'  + entry.name  + '</span>' +
        '<span class="log-meta">x' + entry.quantity + '</span>' +
        '<span class="log-cal">'   + entry.calories + ' kcal</span>' +
        '<button class="log-del" data-id="' + entry.entry_id + '">x</button>';
      row.querySelector('.log-del').onclick = function(e) {
        fetch('/api/log/' + e.currentTarget.dataset.id, { method: 'DELETE' }).then(function() { loadLog(); loadWeekly(); showToast('Entry removed'); });
      };
      sec.appendChild(row);
    });
    container.appendChild(sec);
  });

  if (!hasAny) container.innerHTML = '<div class="empty-log">No food logged yet. Add something from the right.</div>';
}

// ── Weekly chart ──────────────────────────────────────────────
async function loadWeekly() {
  var res = await fetch('/api/weekly');
  var days = await res.json();
  var max = Math.max.apply(null, days.map(function(d) { return d.calories; }).concat([1]));
  var chart = $('barChart');
  chart.innerHTML = '';
  var todayStr = isoDate(new Date());
  days.forEach(function(d) {
    var h = Math.max((d.calories / max) * 68, d.calories > 0 ? 4 : 2);
    var col = document.createElement('div');
    col.className = 'bar-col';
    col.innerHTML = '<div class="bar' + (d.date === todayStr ? ' today' : '') + '" style="height:' + h + 'px"></div><span class="bar-day">' + d.day + '</span>';
    chart.appendChild(col);
  });
}

// ── Categories & foods ────────────────────────────────────────
async function loadCategories() {
  var res = await fetch('/api/categories');
  var cats = await res.json();
  var wrap = $('categoryFilters');
  wrap.innerHTML = '';

  var allBtn = document.createElement('button');
  allBtn.className = 'cat-pill active';
  allBtn.textContent = 'All';
  allBtn.onclick = function() {
    activeCategory = '';
    document.querySelectorAll('.cat-pill').forEach(function(b) { b.classList.remove('active'); });
    allBtn.classList.add('active');
    renderFoods(allFoods);
  };
  wrap.appendChild(allBtn);

  cats.forEach(function(cat) {
    var btn = document.createElement('button');
    btn.className = 'cat-pill';
    btn.textContent = cat.split(' & ')[0];
    btn.onclick = function() {
      activeCategory = cat;
      document.querySelectorAll('.cat-pill').forEach(function(b) { b.classList.remove('active'); });
      btn.classList.add('active');
      renderFoods(allFoods.filter(function(f) { return f.category === cat; }));
    };
    wrap.appendChild(btn);
  });
}

async function loadFoods() {
  var res = await fetch('/api/foods');
  allFoods = await res.json();
  renderFoods(allFoods);
}

function renderFoods(foods) {
  var grid = $('foodGrid');
  grid.innerHTML = '';
  if (!foods.length) { grid.innerHTML = '<p style="color:var(--ink3);grid-column:1/-1;padding:1rem 0">No foods found</p>'; return; }
  foods.forEach(function(food) {
    var card = document.createElement('div');
    card.className = 'food-card';
    card.innerHTML =
      '<div class="food-card-emoji">' + food.emoji + '</div>' +
      '<div class="food-card-name">'  + food.name  + '</div>' +
      '<div class="food-card-cal">'   + food.calories + ' kcal</div>' +
      '<div class="food-card-unit">'  + food.unit  + '</div>';
    card.onclick = function() { openModal(food); };
    grid.appendChild(card);
  });
}

$('searchInput').oninput = function(e) {
  var q = e.target.value.toLowerCase();
  var pool = activeCategory ? allFoods.filter(function(f) { return f.category === activeCategory; }) : allFoods;
  renderFoods(q ? pool.filter(function(f) { return f.name.toLowerCase().includes(q); }) : pool);
};

// ── Init ──────────────────────────────────────────────────────
updateDateLabel();
loadCategories();
loadFoods();
loadLog();
loadWeekly();