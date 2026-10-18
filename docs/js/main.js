/* Главная страница: карта + список маршрутов */
const CATEGORY_COLORS = {
  'Отличный':      '#2e7d32',
  'Благоприятный': '#43a047',
  'Умеренный':     '#ef6c00',
  'Сложный':       '#c62828'
};

const state = {
  routes: [],
  layers: new Map(),       // id -> { layer, route }
  activeCategory: 'all',
  map: null
};

document.addEventListener('DOMContentLoaded', init);

async function init() {
  initMap();
  try {
    await loadRoutes();
    renderCards();
    renderStats();
  } catch (err) {
    console.error(err);
    document.getElementById('error-banner').hidden = false;
  }
}

function initMap() {
  state.map = L.map('map', {
    zoomControl: true,
    scrollWheelZoom: true
  }).setView([56.30, 43.95], 12);

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
  }).addTo(state.map);
}

async function loadRoutes() {
  const res = await fetch('data/routes.json');
  if (!res.ok) throw new Error('routes.json: ' + res.status);
  const data = await res.json();
  state.routes = data.routes;

  // Загружаем геометрию параллельно
  const geometries = await Promise.all(
    state.routes.map(r =>
      fetch(r.geometry_file)
        .then(res => {
          if (!res.ok) throw new Error(r.geometry_file + ': ' + res.status);
          return res.json();
        })
        .then(geo => ({ route: r, geo }))
    )
  );

  const allLayers = [];
  for (const { route, geo } of geometries) {
    const color = CATEGORY_COLORS[route.category] || CATEGORY_COLORS['Благоприятный'];
    const layer = L.geoJSON(geo, {
      style: {
        color,
        weight: 5,
        opacity: 0.85,
        lineCap: 'round',
        lineJoin: 'round'
      },
      onEachFeature: (feature, lyr) => {
        lyr.bindPopup(
          `<strong>${route.name}</strong><br>` +
          `${route.length_km} км · ${route.category}<br>` +
          `<em>${route.district}</em>`
        );
        lyr.on('click', () => {
          window.location.href = `route.html?id=${encodeURIComponent(route.id)}`;
        });
        lyr.on('mouseover', () => lyr.setStyle({ weight: 8 }));
        lyr.on('mouseout', () => lyr.setStyle({ weight: 5 }));
      }
    }).addTo(state.map);

    state.layers.set(route.id, { layer, route });
    allLayers.push(layer);
  }

  if (allLayers.length) {
    const group = L.featureGroup(allLayers);
    state.map.fitBounds(group.getBounds().pad(0.08));
  }
}

function renderCards() {
  const grid = document.getElementById('routes-grid');
  const list = state.activeCategory === 'all'
    ? state.routes
    : state.routes.filter(r => r.category === state.activeCategory);

  if (!list.length) {
    grid.innerHTML = '<p style="color:#64748b">Маршрутов в этой категории нет.</p>';
    return;
  }

  grid.innerHTML = list.map(r => {
    const color = CATEGORY_COLORS[r.category] || CATEGORY_COLORS['Благоприятный'];
    return `
      <article class="route-card" data-id="${r.id}" style="--accent-route:${color}">
        <div class="route-card__head">
          <span class="badge" style="background:${color}">${r.category}</span>
          <span class="route-card__length">${r.length_km} км</span>
        </div>
        <h3>${r.name}</h3>
        <p class="route-card__district">${r.district}</p>
        <div class="route-card__stats">
          <span>Безопасность: ${r.safety}/3</span>
          <span>Рельеф: ${r.difficulty}/3</span>
          <span>Привлекательность: ${r.attractiveness}/3</span>
          <span>Покрытие: ${r.surface}/3</span>
        </div>
        <div class="route-card__score">Оценка: ${r.total}/12</div>
        <a class="btn" href="route.html?id=${encodeURIComponent(r.id)}">Подробнее</a>
      </article>
    `;
  }).join('');

  // Подсветка маршрута на карте при наведении на карточку
  grid.querySelectorAll('.route-card').forEach(card => {
    card.addEventListener('mouseenter', () => setLayerWeight(card.dataset.id, 8));
    card.addEventListener('mouseleave', () => setLayerWeight(card.dataset.id, 5));
  });
}

function setLayerWeight(id, weight) {
  const item = state.layers.get(id);
  if (item) item.layer.setStyle({ weight });
}

function renderStats() {
  const count = state.routes.length;
  const totalLength = state.routes.reduce((sum, r) => sum + (r.length_km || 0), 0);
  const best = state.routes.reduce((max, r) => Math.max(max, r.total || 0), 0);

  document.getElementById('stat-count').textContent = count;
  document.getElementById('stat-length').textContent = totalLength.toFixed(1);
  document.getElementById('stat-best').textContent = best + '/12';
}

/* Фильтры по категориям */
document.addEventListener('click', (e) => {
  const btn = e.target.closest('.filter');
  if (!btn) return;
  document.querySelectorAll('.filter').forEach(b => b.classList.remove('is-active'));
  btn.classList.add('is-active');
  state.activeCategory = btn.dataset.category;
  renderCards();

  // Показать только маршруты выбранной категории на карте
  state.layers.forEach(({ layer, route }) => {
    const visible = state.activeCategory === 'all' || route.category === state.activeCategory;
    if (visible) {
      if (!state.map.hasLayer(layer)) layer.addTo(state.map);
    } else {
      if (state.map.hasLayer(layer)) state.map.removeLayer(layer);
    }
  });
});