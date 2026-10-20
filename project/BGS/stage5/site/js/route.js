/* Страница отдельного маршрута */
const CATEGORY_COLORS = {
  'Отличный':      '#2e7d32',
  'Благоприятный': '#43a047',
  'Умеренный':     '#ef6c00',
  'Сложный':       '#c62828'
};

document.addEventListener('DOMContentLoaded', init);

async function init() {
  const id = new URLSearchParams(location.search).get('id');
  if (!id) {
    location.replace('index.html');
    return;
  }

  try {
    const [routesRes, geoRes] = await Promise.all([
      fetch('data/routes.json'),
      // геометрию подгрузим после того, как узнаем имя файла
      Promise.resolve(null)
    ]);

    if (!routesRes.ok) throw new Error('routes.json');
    const data = await routesRes.json();
    const route = data.routes.find(r => r.id === id);
    if (!route) throw new Error('Маршрут не найден');

    document.title = `${route.name} — Маршруты Нижнего Новгорода`;

    const geoResponse = await fetch(route.geometry_file);
    if (!geoResponse.ok) throw new Error('geometry: ' + geoResponse.status);
    const geo = await geoResponse.json();

    renderRoute(route, geo);
    document.getElementById('route-loading').hidden = true;
    document.getElementById('route-content').hidden = false;
  } catch (err) {
    console.error(err);
    document.getElementById('route-loading').textContent =
      'Не удалось загрузить маршрут. Проверьте, что сайт открыт через локальный сервер.';
  }
}

function renderRoute(route, geo) {
  const color = CATEGORY_COLORS[route.category] || CATEGORY_COLORS['Благоприятный'];

  // Бейдж
  const badge = document.getElementById('route-badge');
  badge.textContent = route.category;
  badge.style.background = color;

  // Заголовок и основные данные
  document.getElementById('route-title').textContent = route.name;
  document.getElementById('route-district').textContent = route.district;
  document.getElementById('route-length').textContent = route.length_km;
  document.getElementById('route-total').textContent = route.total;

  // Оценки
  document.getElementById('route-scores').innerHTML = [
    scoreBar('Безопасность', route.safety),
    scoreBar('Рельеф', route.difficulty),
    scoreBar('Привлекательность', route.attractiveness),
    scoreBar('Покрытие', route.surface)
  ].join('');

  // Тексты
  document.getElementById('route-description').textContent = route.description;
  document.getElementById('route-pros').textContent = route.pros;
  document.getElementById('route-cons').textContent = route.cons;
  document.getElementById('route-sights').textContent = route.sights;

  // Галерея
  renderGallery(route.photos || []);

  // Карта
  const map = L.map('route-map',{zoomControl: true}, { scrollWheelZoom: true }).setView([56.30, 43.95], 13);
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
  }).addTo(map);

  const layer = L.geoJSON(geo, {
    style: {
      color,
      weight: 6,
      opacity: 0.9,
      lineCap: 'round',
      lineJoin: 'round'
    }
  }).addTo(map);

  // Точки старта и финиша
  const coords = extractFirstLineCoords(geo);
  if (coords.length) {
    const start = coords[0];
    const end = coords[coords.length - 1];
    L.circleMarker([start[1], start[0]], {
      radius: 7, color: '#fff', weight: 3, fillColor: '#2e7d32', fillOpacity: 1
    }).addTo(map).bindPopup('Старт');
    L.circleMarker([end[1], end[0]], {
      radius: 7, color: '#fff', weight: 3, fillColor: '#c62828', fillOpacity: 1
    }).addTo(map).bindPopup('Финиш');
  }

  map.fitBounds(layer.getBounds().pad(0.1));

  // Небольшой «толчок» для Leaflet, если карта в скрытом контейнере
  setTimeout(() => map.invalidateSize(), 120);
}

function scoreBar(label, value) {
  const pct = Math.max(0, Math.min(3, value)) / 3 * 100;
  return `
    <div class="score">
      <div class="score__label">${label}<span>${value}/3</span></div>
      <div class="score__bar"><div style="width:${pct}%"></div></div>
    </div>
  `;
}

function renderGallery(photos) {
  const el = document.getElementById('route-gallery');
  if (!photos.length) {
    el.innerHTML = '<div class="gallery__empty">Фотографии этого маршрута скоро появятся.</div>';
    return;
  }
  el.innerHTML = photos.map(src =>
    `<img src="${src}" alt="Фото маршрута" loading="lazy">`
  ).join('');
}

function extractFirstLineCoords(geo) {
  try {
    const feature = geo.features[0];
    if (feature.geometry.type === 'LineString') return feature.geometry.coordinates;
    if (feature.geometry.type === 'MultiLineString') return feature.geometry.coordinates[0];
  } catch (e) { /* ignore */ }
  return [];
}