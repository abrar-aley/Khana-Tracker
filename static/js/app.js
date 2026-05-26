// ── State ─────────────────────────────────────────────────────
var currentDate = new Date();
var allFoods = [];
var activeCategory = '';
var selectedFood = null;
var selectedMeal = 'Breakfast';
var GOAL = 2000; // will be loaded from server

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

// ── Log food modal ────────────────────────────────────────────
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
  $('modalBackdrop').style.display = 'flex';
}

function closeModal() {
  $('modalBackdrop').style.display = 'none';
  selectedFood = null;
}

function updatePreview() {
  if (!selectedFood) return;
  var qty = parseFloat($('qtyInput').value) || 1;
  $('previewCal').textContent = Math.round(selectedFood.calories * qty);
  $('previewP').textContent   = Math.round(selectedFood.protein  * qty * 10) / 10;
  $('previewC').textContent   = Math.round(selectedFood.carbs    * qty * 10) / 10;
  $('previewF').textContent   = Math.round(selectedFood.fat      * qty * 10) / 10;
}

$('modalClose').onclick = function(e) { e.stopPropagation(); closeModal(); };
$('modalBackdrop').onclick = function(e) { if (e.target === $('modalBackdrop')) closeModal(); };

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
  var name = selectedFood.name;
  var emoji = selectedFood.emoji;
  await fetch('/api/log', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ food_id: selectedFood.id, quantity: qty, meal: selectedMeal, date: isoDate(currentDate) })
  });
  closeModal();
  loadLog();
  loadWeekly();
  showToast(emoji + ' ' + name + ' logged!');
};

// ── Custom food modal ─────────────────────────────────────────
$('openCustomFood').onclick = function() {
  $('cfName').value = '';
  $('cfUnit').value = '100g';
  $('cfCalories').value = '';
  $('cfProtein').value = '';
  $('cfCarbs').value = '';
  $('cfFat').value = '';
  $('cfCategory').value = 'Custom';
  $('customFoodBackdrop').style.display = 'flex';
};

$('customFoodClose').onclick = function(e) {
  e.stopPropagation();
  $('customFoodBackdrop').style.display = 'none';
};

$('customFoodBackdrop').onclick = function(e) {
  if (e.target === $('customFoodBackdrop')) $('customFoodBackdrop').style.display = 'none';
};

$('confirmCustomFood').onclick = async function() {
  var name = $('cfName').value.trim();
  if (!name) { showToast('Please enter a food name!'); return; }

  var res = await fetch('/api/foods/custom', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      name:     name,
      category: $('cfCategory').value,
      unit:     $('cfUnit').value.trim() || '100g',
      calories: parseFloat($('cfCalories').value) || 0,
      protein:  parseFloat($('cfProtein').value)  || 0,
      carbs:    parseFloat($('cfCarbs').value)    || 0,
      fat:      parseFloat($('cfFat').value)      || 0,
    })
  });

  if (res.ok) {
    $('customFoodBackdrop').style.display = 'none';
    showToast('Food added successfully!');
    loadFoods();
    loadCategories();
  } else {
    showToast('Error saving food!');
  }
};

document.onkeydown = function(e) {
  if (e.key === 'Escape') {
    closeModal();
    $('customFoodBackdrop').style.display = 'none';
  }
};

// ── Date nav ──────────────────────────────────────────────────
function updateDateLabel() {
  var today = new Date(); today.setHours(0,0,0,0);
  var cur = new Date(currentDate); cur.setHours(0,0,0,0);
  var diff = Math.round((cur - today) / 86400000);
  $('currentDate').textContent = diff === 0 ? 'Today' : diff === -1 ? 'Yesterday' : fmtDate(currentDate);
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
        fetch('/api/log/' + e.currentTarget.dataset.id, { method: 'DELETE' })
          .then(function() { loadLog(); loadWeekly(); showToast('Entry removed'); });
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
  var pool = activeCategory ? allFoods.filter(function(f) { return f.category === activeCategory; }) : allFoods;
  renderFoods(pool);
}

function renderFoods(foods) {
  var grid = $('foodGrid');
  grid.innerHTML = '';
  if (!foods.length) {
    grid.innerHTML = '<p style="color:var(--ink3);grid-column:1/-1;padding:1rem 0">No foods found</p>';
    return;
  }
  foods.forEach(function(food) {
    var card = document.createElement('div');
    card.className = 'food-card' + (food.is_custom ? ' custom-card' : '');
    card.innerHTML =
      (food.is_custom ? '<span class="custom-badge">Custom</span>' : '') +
      '<div class="food-card-emoji">' + food.emoji + '</div>' +
      '<div class="food-card-name">'  + food.name  + '</div>' +
      '<div class="food-card-cal">'   + food.calories + ' kcal</div>' +
      '<div class="food-card-unit">'  + food.unit  + '</div>' +
      (food.is_custom ? '<button class="del-custom" data-id="' + food.id + '">Delete</button>' : '');

    card.onclick = function(e) {
      if (e.target.classList.contains('del-custom')) return;
      openModal(food);
    };

    if (food.is_custom) {
      card.querySelector('.del-custom').onclick = function(e) {
        e.stopPropagation();
        if (confirm('Delete ' + food.name + '?')) {
          fetch('/api/foods/custom/' + food.id, { method: 'DELETE' })
            .then(function() { loadFoods(); loadCategories(); showToast(food.name + ' deleted'); });
        }
      };
    }
    grid.appendChild(card);
  });
}

$('searchInput').oninput = function(e) {
  var q = e.target.value.toLowerCase();
  var pool = activeCategory ? allFoods.filter(function(f) { return f.category === activeCategory; }) : allFoods;
  renderFoods(q ? pool.filter(function(f) { return f.name.toLowerCase().includes(q); }) : pool);
};

// ── Init ──────────────────────────────────────────────────────
loadGoal();
updateDateLabel();
loadCategories();
loadFoods();
loadLog();
loadWeekly();

// ── Goal setting ──────────────────────────────────────────────
async function loadGoal() {
  var res = await fetch('/api/settings/goal');
  var data = await res.json();
  GOAL = data.goal;
  $('goalLabel').textContent = '/ ' + GOAL + ' goal';
  $('goalInput').value = GOAL;
}

function setQuickGoal(val) {
  $('goalInput').value = val;
}

$('openGoal').onclick = function() {
  $('goalInput').value = GOAL;
  $('goalBackdrop').style.display = 'flex';
};

$('goalClose').onclick = function(e) {
  e.stopPropagation();
  $('goalBackdrop').style.display = 'none';
};

$('goalBackdrop').onclick = function(e) {
  if (e.target === $('goalBackdrop')) $('goalBackdrop').style.display = 'none';
};

$('confirmGoal').onclick = async function() {
  var goal = parseInt($('goalInput').value);
  if (!goal || goal < 100 || goal > 10000) {
    showToast('Please enter a goal between 100 and 10000!');
    return;
  }
  var res = await fetch('/api/settings/goal', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ goal: goal })
  });
  if (res.ok) {
    GOAL = goal;
    $('goalLabel').textContent = '/ ' + GOAL + ' goal';
    $('goalBackdrop').style.display = 'none';
    loadLog();
    showToast('Goal set to ' + GOAL + ' kcal!');
  }
};

// ── BMI & Weight tracker ──────────────────────────────────────
var userHeight = null;

function calcBMI(weight, height) {
  if (!weight || !height) return null;
  return Math.round((weight / Math.pow(height / 100, 2)) * 10) / 10;
}

function bmiCategory(bmi) {
  if (bmi < 18.5) return { text: 'Underweight', cls: 'underweight' };
  if (bmi < 25)   return { text: 'Normal', cls: 'normal' };
  if (bmi < 30)   return { text: 'Overweight', cls: 'overweight' };
  return { text: 'Obese', cls: 'obese' };
}

function updateBMIDisplay(weight) {
  var bmi = calcBMI(weight, userHeight);
  if (bmi) {
    $('bmiValue').textContent = bmi;
    var cat = bmiCategory(bmi);
    $('bmiCat').textContent = cat.text;
    $('bmiCat').className = 'bmi-cat ' + cat.cls;
  } else {
    $('bmiValue').textContent = '--';
    $('bmiCat').textContent = 'Enter height & weight';
    $('bmiCat').className = 'bmi-cat';
  }
}

async function loadHeight() {
  var res = await fetch('/api/settings/height');
  var data = await res.json();
  if (data.height) {
    userHeight = data.height;
    $('heightInput').value = data.height;
  }
}

async function loadWeightLog() {
  var res = await fetch('/api/weight');
  var entries = await res.json();

  if (entries.length > 0) {
    var latest = entries[0];
    $('currentWeight').textContent = latest.weight + ' kg';
    $('weightInput').value = latest.weight;
    updateBMIDisplay(latest.weight);
  }

  // Draw weight chart (last 10 entries, reversed to show oldest first)
  var chart = $('weightChart');
  chart.innerHTML = '';
  if (entries.length === 0) {
    chart.innerHTML = '<p style="color:var(--ink3);font-size:.78rem">No weight logged yet</p>';
    return;
  }

  var reversed = entries.slice(0, 10).reverse();
  var weights = reversed.map(function(e) { return e.weight; });
  var minW = Math.min.apply(null, weights);
  var maxW = Math.max.apply(null, weights);
  var range = maxW - minW || 1;
  var todayStr = isoDate(new Date());

  reversed.forEach(function(e) {
    var h = Math.max(((e.weight - minW) / range) * 48 + 8, 8);
    var day = e.date.slice(5); // MM-DD
    var col = document.createElement('div');
    col.className = 'w-bar-col';
    col.innerHTML =
      '<span class="w-bar-val">' + e.weight + '</span>' +
      '<div class="w-bar' + (e.date === todayStr ? ' today' : '') + '" style="height:' + h + 'px" title="' + e.weight + ' kg on ' + e.date + '"></div>' +
      '<span class="w-bar-day">' + day + '</span>';
    chart.appendChild(col);
  });
}

$('saveHeight').onclick = async function() {
  var h = parseFloat($('heightInput').value);
  if (!h || h < 50 || h > 300) { showToast('Please enter a valid height!'); return; }
  var res = await fetch('/api/settings/height', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ height: h })
  });
  if (res.ok) {
    userHeight = h;
    showToast('Height saved: ' + h + ' cm');
    var w = parseFloat($('weightInput').value);
    if (w) updateBMIDisplay(w);
  }
};

$('saveWeight').onclick = async function() {
  var w = parseFloat($('weightInput').value);
  if (!w || w <= 0 || w > 500) { showToast('Please enter a valid weight!'); return; }
  var res = await fetch('/api/weight', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ weight: w, date: isoDate(currentDate) })
  });
  if (res.ok) {
    showToast('Weight logged: ' + w + ' kg');
    loadWeightLog();
  }
};

// Add to init
loadHeight();
loadWeightLog();