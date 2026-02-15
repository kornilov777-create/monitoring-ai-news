/**
 * Moscow Guide - Static Frontend (GitHub Pages)
 * Top 100 restaurants & events in Moscow
 * Data loaded from embedded data.js
 */

// State
let allRestaurants = [];
let allEvents = [];
let currentCategory = 'all';
let currentPrice = 0;
let currentSearch = '';
let currentEventType = 'all';
let currentRestaurant = null;
let bookings = JSON.parse(localStorage.getItem('moscow_bookings') || '[]');

const CATEGORY_LABELS = {
    romantic: 'Свидание',
    celebration: 'Праздник',
    business: 'Бизнес',
    family: 'Семейный',
    rooftop: 'Панорама',
    author_cuisine: 'Авторская кухня',
    asian: 'Азиатская кухня',
    italian: 'Итальянская',
    georgian: 'Грузинская',
    seafood: 'Морепродукты',
    bar: 'Бар',
    budget: 'Бюджетный'
};

const EVENT_TYPE_LABELS = {
    concert: 'Концерт', theatre: 'Театр', exhibition: 'Выставка',
    festival: 'Фестиваль', standup: 'Стендап', party: 'Вечеринка',
    sport: 'Спорт', cinema: 'Кино'
};

const FEATURE_LABELS = {
    terrace: 'Терраса', parking: 'Парковка', kids_room: 'Детская комната',
    live_music: 'Живая музыка', hookah: 'Кальян', private_room: 'VIP-зал',
    wifi: 'Wi-Fi', delivery: 'Доставка', breakfast: 'Завтраки',
    brunch: 'Бранч', banquet: 'Банкеты', bar: 'Бар'
};

const TAG_LABELS = {
    date: 'Свидание', birthday: 'День рождения', corporate: 'Корпоратив',
    terrace: 'Терраса', live_music: 'Живая музыка', michelin: 'Michelin',
    rooftop: 'Крыша', view: 'Вид', cocktails: 'Коктейли',
    wine: 'Винная карта', brunch: 'Бранч', kids: 'С детьми',
    group: 'Для компании', quiet: 'Тихий', late_night: 'Допоздна',
    instagrammable: 'Инстаграмный'
};

// ===== Particle System =====
function initParticles() {
    const canvas = document.getElementById('particleCanvas');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    let particles = [];
    let w, h;

    function resize() {
        w = canvas.width = window.innerWidth;
        h = canvas.height = window.innerHeight;
    }

    function createParticle() {
        return {
            x: Math.random() * w, y: Math.random() * h,
            vx: (Math.random() - 0.5) * 0.3, vy: (Math.random() - 0.5) * 0.3,
            size: Math.random() * 1.5 + 0.5,
            opacity: Math.random() * 0.4 + 0.1,
            hue: Math.random() > 0.5 ? 185 : 300,
        };
    }

    function init() {
        resize();
        particles = [];
        const count = Math.min(80, Math.floor(w * h / 15000));
        for (let i = 0; i < count; i++) particles.push(createParticle());
    }

    function animate() {
        ctx.clearRect(0, 0, w, h);
        for (let i = 0; i < particles.length; i++) {
            const p = particles[i];
            p.x += p.vx; p.y += p.vy;
            if (p.x < 0) p.x = w; if (p.x > w) p.x = 0;
            if (p.y < 0) p.y = h; if (p.y > h) p.y = 0;
            ctx.beginPath();
            ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
            ctx.fillStyle = `hsla(${p.hue}, 100%, 70%, ${p.opacity})`;
            ctx.fill();
            for (let j = i + 1; j < particles.length; j++) {
                const p2 = particles[j];
                const dx = p.x - p2.x, dy = p.y - p2.y;
                const dist = Math.sqrt(dx * dx + dy * dy);
                if (dist < 150) {
                    ctx.beginPath();
                    ctx.moveTo(p.x, p.y);
                    ctx.lineTo(p2.x, p2.y);
                    ctx.strokeStyle = `hsla(185, 100%, 70%, ${(1 - dist / 150) * 0.08})`;
                    ctx.lineWidth = 0.5;
                    ctx.stroke();
                }
            }
        }
        requestAnimationFrame(animate);
    }

    window.addEventListener('resize', resize);
    init();
    animate();
}

// ===== Init =====
document.addEventListener('DOMContentLoaded', () => {
    initParticles();
    loadRestaurants();
    loadEvents();
    setupScrollListener();
    setDefaultBookingDate();
    animateCounters();
});

function animateCounters() {
    document.querySelectorAll('.hero-stat-number').forEach(counter => {
        const target = parseInt(counter.textContent);
        if (isNaN(target) || target === 0) return;
        let current = 0;
        const step = Math.max(1, Math.floor(target / 40));
        const interval = setInterval(() => {
            current += step;
            if (current >= target) { current = target; clearInterval(interval); }
            counter.textContent = current;
        }, 30);
    });
}

// ===== Data Loading (from embedded data.js) =====
function loadRestaurants() {
    try {
        // Assign UUIDs if missing
        allRestaurants = (typeof RESTAURANT_DATA !== 'undefined' ? RESTAURANT_DATA : []).map((r, i) => {
            if (!r.id) r.id = 'r-' + i;
            return r;
        });
        // Sort by rating desc
        allRestaurants.sort((a, b) => (b.rating || 0) - (a.rating || 0));
        document.getElementById('statRestaurants').textContent = allRestaurants.length;
        renderFeatured();
        renderRestaurants();
    } catch (e) {
        console.error('Error loading restaurants:', e);
        document.getElementById('restaurantsLoading').style.display = 'none';
        showToast('Ошибка загрузки ресторанов', 'error');
    }
}

function loadEvents() {
    // Events will be empty in static mode (no KudaGo API on client)
    allEvents = [];
    document.getElementById('statEvents').textContent = '0';
    document.getElementById('eventsLoading').style.display = 'none';
    document.getElementById('eventsEmpty').style.display = 'block';
}

// ===== Render =====
function renderFeatured() {
    const featured = allRestaurants.filter(r => r.is_featured).slice(0, 5);
    const container = document.getElementById('featuredCarousel');
    if (featured.length === 0) {
        document.getElementById('featuredSection').style.display = 'none';
        return;
    }
    container.innerHTML = featured.map(r => `
        <div class="featured-card" onclick="openRestaurantModal('${r.slug}')">
            <div class="featured-card-photo" style="background-image: url('${getPhotoUrl(r)}')">
                <span class="featured-badge">TOP</span>
                <span class="featured-rating">${r.rating.toFixed(1)}</span>
            </div>
            <div class="featured-card-body">
                <div class="featured-card-name">${r.name}</div>
                <div class="featured-card-cuisine">${(r.cuisine_type||[]).join(' / ')}</div>
                <div class="featured-card-meta">
                    <span>
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/></svg>
                        ${r.metro_station || r.address}
                    </span>
                    <span>${getPriceSymbol(r.price_level)}</span>
                </div>
            </div>
        </div>
    `).join('');
}

function renderRestaurants() {
    const container = document.getElementById('restaurantGrid');
    const loading = document.getElementById('restaurantsLoading');
    const empty = document.getElementById('restaurantsEmpty');

    let filtered = allRestaurants;
    if (currentCategory !== 'all') filtered = filtered.filter(r => r.category === currentCategory);
    if (currentPrice > 0) filtered = filtered.filter(r => r.price_level === currentPrice);
    if (currentSearch) {
        const q = currentSearch.toLowerCase();
        filtered = filtered.filter(r =>
            r.name.toLowerCase().includes(q) ||
            (r.description && r.description.toLowerCase().includes(q)) ||
            (r.metro_station && r.metro_station.toLowerCase().includes(q)) ||
            r.address.toLowerCase().includes(q) ||
            (r.cuisine_type||[]).some(c => c.toLowerCase().includes(q)) ||
            (r.tags||[]).some(t => t.toLowerCase().includes(q))
        );
    }

    loading.style.display = 'none';
    if (filtered.length === 0) { container.innerHTML = ''; empty.style.display = 'block'; return; }

    empty.style.display = 'none';
    container.innerHTML = filtered.map((r, i) => `
        <div class="restaurant-card" onclick="openRestaurantModal('${r.slug}')" style="animation: fadeInUp 0.4s ease ${Math.min(i * 0.03, 1)}s both;">
            <div class="card-photo" style="background-image: url('${getPhotoUrl(r)}')">
                <span class="card-rating">${r.rating.toFixed(1)}</span>
                <span class="card-price-badge">${getPriceSymbol(r.price_level)}</span>
            </div>
            <div class="card-body">
                <div class="card-name">${r.name}</div>
                <div class="card-cuisine">${(r.cuisine_type||[]).join(' / ')}</div>
                <div class="card-description">${r.short_description || ''}</div>
                <div class="card-meta">
                    <span class="card-location">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/></svg>
                        ${r.metro_station || ''}
                    </span>
                    <span class="card-check">${r.avg_check ? formatPrice(r.avg_check) + ' ₽' : ''}</span>
                </div>
                <div class="card-tags">
                    ${(r.tags||[]).slice(0, 3).map(t => `<span class="card-tag">${TAG_LABELS[t] || t}</span>`).join('')}
                </div>
            </div>
        </div>
    `).join('');
}

// Inject fadeInUp animation
const _s = document.createElement('style');
_s.textContent = '@keyframes fadeInUp{from{opacity:0;transform:translateY(20px)}to{opacity:1;transform:translateY(0)}}';
document.head.appendChild(_s);

function renderEvents() {
    const container = document.getElementById('eventsGrid');
    const loading = document.getElementById('eventsLoading');
    const empty = document.getElementById('eventsEmpty');
    let filtered = allEvents;
    if (currentEventType !== 'all') filtered = filtered.filter(e => e.event_type === currentEventType);
    loading.style.display = 'none';
    if (filtered.length === 0) { container.innerHTML = ''; empty.style.display = 'block'; return; }
    empty.style.display = 'none';
    container.innerHTML = filtered.map(e => `
        <div class="event-card" onclick="openEventModal('${e.id}')">
            <div class="event-photo" style="background-image: url('${e.photo_url || getEventPlaceholder(e.event_type)}')">
                <span class="event-type-badge">${EVENT_TYPE_LABELS[e.event_type] || e.event_type}</span>
                ${e.date_start ? `<span class="event-date-badge">${formatEventDate(e.date_start)}</span>` : ''}
            </div>
            <div class="event-body">
                <div class="event-title">${e.title}</div>
                <div class="event-venue">${e.venue_name || ''} ${e.address ? '· ' + e.address : ''}</div>
                <div class="event-price">${formatEventPrice(e)}</div>
            </div>
        </div>
    `).join('');
}

// ===== Modal =====
function openRestaurantModal(slug) {
    const r = allRestaurants.find(r => r.slug === slug);
    if (!r) return;
    currentRestaurant = r;

    document.getElementById('modalPhoto').style.backgroundImage = `url('${getPhotoUrl(r)}')`;
    document.getElementById('modalRating').textContent = r.rating.toFixed(1);
    document.getElementById('modalTitle').textContent = r.name;
    document.getElementById('modalCategory').textContent = CATEGORY_LABELS[r.category] || r.category;
    document.getElementById('modalPrice').textContent = getPriceSymbol(r.price_level);
    document.getElementById('modalCheck').textContent = r.avg_check ? `~${formatPrice(r.avg_check)} ₽` : '';
    document.getElementById('modalDescription').textContent = r.description || '';
    document.getElementById('modalAddress').textContent = r.address;
    document.getElementById('modalMetro').textContent = r.metro_station || 'Не указано';
    document.getElementById('modalPhone').textContent = r.phone || 'Не указан';
    document.getElementById('modalHours').textContent = formatWorkingHours(r.working_hours);

    document.getElementById('modalTags').innerHTML = (r.tags||[]).map(t =>
        `<span class="modal-tag">${TAG_LABELS[t] || t}</span>`
    ).join('');

    const features = r.features || {};
    document.getElementById('modalFeatures').innerHTML = Object.entries(features)
        .filter(([_, v]) => v)
        .map(([k]) => `<span class="feature-badge">✓ ${FEATURE_LABELS[k] || k}</span>`)
        .join('');

    if (r.cuisine_type && r.cuisine_type.length > 0) {
        document.getElementById('modalCuisine').innerHTML = `
            <div class="cuisine-label">Кухня</div>
            <div class="cuisine-tags">${r.cuisine_type.map(c => `<span class="cuisine-tag">${c}</span>`).join('')}</div>
        `;
    } else {
        document.getElementById('modalCuisine').innerHTML = '';
    }

    const websiteBtn = document.getElementById('modalWebsite');
    const callBtn = document.getElementById('modalCall');
    websiteBtn.style.display = r.website_url ? 'inline-flex' : 'none';
    if (r.website_url) websiteBtn.href = r.website_url;
    callBtn.style.display = r.phone ? 'inline-flex' : 'none';
    if (r.phone) callBtn.href = `tel:${r.phone.replace(/[^\d+]/g, '')}`;

    document.getElementById('bookingRestaurantId').value = r.id;
    document.getElementById('bookingFormContainer').style.display = 'none';
    document.getElementById('bookingSuccess').style.display = 'none';

    document.getElementById('restaurantModal').classList.add('active');
    document.body.style.overflow = 'hidden';
}

function closeRestaurantModal() {
    document.getElementById('restaurantModal').classList.remove('active');
    document.body.style.overflow = '';
    currentRestaurant = null;
}

function openEventModal(eventId) {
    const e = allEvents.find(ev => ev.id === eventId);
    if (!e) return;
    document.getElementById('eventModalPhoto').style.backgroundImage = `url('${e.photo_url || getEventPlaceholder(e.event_type)}')`;
    document.getElementById('eventModalTitle').textContent = e.title;
    document.getElementById('eventModalType').textContent = EVENT_TYPE_LABELS[e.event_type] || e.event_type;
    document.getElementById('eventModalPrice').textContent = formatEventPrice(e);
    document.getElementById('eventModalDescription').textContent = e.description || e.short_description || '';
    document.getElementById('eventModalDate').textContent = e.date_start ? formatEventDateFull(e.date_start, e.date_end) : 'Дата уточняется';
    document.getElementById('eventModalVenue').textContent = `${e.venue_name || ''} ${e.address ? '· ' + e.address : ''}`;
    const ticketBtn = document.getElementById('eventModalTicket');
    ticketBtn.style.display = e.ticket_url ? 'inline-flex' : 'none';
    if (e.ticket_url) ticketBtn.href = e.ticket_url;
    document.getElementById('eventModal').classList.add('active');
    document.body.style.overflow = 'hidden';
}

function closeEventModal() {
    document.getElementById('eventModal').classList.remove('active');
    document.body.style.overflow = '';
}

function closeModal(event) {
    if (event.target.classList.contains('modal-overlay')) {
        event.target.classList.remove('active');
        document.body.style.overflow = '';
    }
}

// ===== Booking (saves to localStorage in static mode) =====
function showBookingForm() {
    document.getElementById('bookingFormContainer').style.display = 'block';
    document.getElementById('bookingFormContainer').scrollIntoView({ behavior: 'smooth', block: 'center' });
}

async function submitBooking(event) {
    event.preventDefault();
    const btn = document.getElementById('bookingSubmitBtn');
    btn.disabled = true;
    btn.textContent = 'Сохраняем...';

    const booking = {
        id: 'b-' + Date.now(),
        restaurant_id: document.getElementById('bookingRestaurantId').value,
        restaurant_name: currentRestaurant ? currentRestaurant.name : '',
        guest_name: document.getElementById('bookingName').value,
        guest_phone: document.getElementById('bookingPhone').value,
        guest_email: document.getElementById('bookingEmail').value || null,
        date: document.getElementById('bookingDate').value,
        time: document.getElementById('bookingTime').value + ':00',
        guests_count: parseInt(document.getElementById('bookingGuests').value),
        special_requests: document.getElementById('bookingRequests').value || null,
        status: 'pending',
        created_at: new Date().toISOString(),
    };

    // Save locally
    bookings.push(booking);
    localStorage.setItem('moscow_bookings', JSON.stringify(bookings));

    document.getElementById('bookingFormContainer').style.display = 'none';
    document.getElementById('bookingSuccess').style.display = 'block';
    document.getElementById('bookingForm').reset();
    setDefaultBookingDate();
    showToast('Бронирование сохранено!', 'success');

    btn.disabled = false;
    btn.textContent = 'Отправить бронь';
}

// ===== Filters =====
function filterByCategory(category, element) {
    currentCategory = category;
    document.querySelectorAll('[data-category]').forEach(el => el.classList.remove('active'));
    element.classList.add('active');
    renderRestaurants();
}

function filterByPrice(price, element) {
    currentPrice = price;
    document.querySelectorAll('.price-chip').forEach(el => el.classList.remove('active'));
    element.classList.add('active');
    renderRestaurants();
}

function filterByEventType(type, element) {
    currentEventType = type;
    document.querySelectorAll('[data-event-type]').forEach(el => el.classList.remove('active'));
    element.classList.add('active');
    renderEvents();
}

// ===== Search =====
function toggleSearch() {
    const bar = document.getElementById('searchBar');
    bar.classList.toggle('active');
    if (bar.classList.contains('active')) document.getElementById('searchInput').focus();
}

function handleSearch(value) { currentSearch = value; renderRestaurants(); }

function clearSearch() {
    document.getElementById('searchInput').value = '';
    currentSearch = '';
    renderRestaurants();
    document.getElementById('searchBar').classList.remove('active');
}

// ===== Navigation =====
document.querySelectorAll('.nav-link').forEach(link => {
    link.addEventListener('click', function(e) {
        e.preventDefault();
        const section = this.dataset.section;
        document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
        this.classList.add('active');
        document.querySelectorAll('.section').forEach(s => s.style.display = 'none');
        document.getElementById(`${section}-section`).style.display = 'block';
        if (section === 'bookings') renderBookings();
        document.getElementById(`${section}-section`).scrollIntoView({ behavior: 'smooth' });
    });
});

function renderBookings() {
    const container = document.getElementById('bookingsList');
    if (bookings.length === 0) return;
    container.innerHTML = bookings.map(b => `
        <div class="booking-item">
            <div class="booking-item-info">
                <h4>${b.restaurant_name}</h4>
                <p>${formatDate(b.date)} в ${b.time ? b.time.slice(0, 5) : ''} · ${b.guests_count} гостей</p>
            </div>
            <span class="booking-item-status ${b.status}">${
                b.status === 'pending' ? 'Ожидает' :
                b.status === 'confirmed' ? 'Подтверждено' : 'Отменено'
            }</span>
        </div>
    `).join('');
}

// ===== Utilities =====
function getPhotoUrl(r) {
    if (r.photo_url) return r.photo_url;
    return `https://via.placeholder.com/800x500/0a0a1a/00f0ff?text=${encodeURIComponent(r.name)}`;
}

function getEventPlaceholder(type) {
    const colors = { concert:'8b5cf6',theatre:'ec4899',exhibition:'3b82f6',festival:'f59e0b',standup:'10b981',party:'ef4444',sport:'06b6d4',cinema:'6366f1' };
    return `https://via.placeholder.com/800x500/${colors[type]||'8b5cf6'}/ffffff?text=${EVENT_TYPE_LABELS[type]||type}`;
}

function getPriceSymbol(level) { return '₽'.repeat(level || 1); }
function formatPrice(num) { return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ' '); }

function formatWorkingHours(hours) {
    if (!hours || Object.keys(hours).length === 0) return 'Уточняйте';
    const days = ['mon','tue','wed','thu','fri','sat','sun'];
    const values = days.map(d => hours[d]).filter(Boolean);
    if (values.length === 0) return 'Уточняйте';
    if (new Set(values).size === 1) return `Ежедневно ${values[0]}`;
    return `Пн-Пт: ${hours.mon || '—'}, Сб-Вс: ${hours.sat || '—'}`;
}

function formatEventDate(dateStr) {
    const d = new Date(dateStr);
    const m = ['янв','фев','мар','апр','мая','июн','июл','авг','сен','окт','ноя','дек'];
    return `${d.getDate()} ${m[d.getMonth()]}`;
}

function formatEventDateFull(start, end) {
    const d = new Date(start);
    const m = ['января','февраля','марта','апреля','мая','июня','июля','августа','сентября','октября','ноября','декабря'];
    let result = `${d.getDate()} ${m[d.getMonth()]} ${d.getFullYear()}`;
    if (end) { const de = new Date(end); if (de.toDateString() !== d.toDateString()) result += ` — ${de.getDate()} ${m[de.getMonth()]}`; }
    return result;
}

function formatEventPrice(e) {
    if (e.is_free) return 'Бесплатно';
    if (e.price_from && e.price_to) return `${formatPrice(e.price_from)} — ${formatPrice(e.price_to)} ₽`;
    if (e.price_from) return `от ${formatPrice(e.price_from)} ₽`;
    return 'Цена уточняется';
}

function formatDate(dateStr) {
    return new Date(dateStr).toLocaleDateString('ru-RU', { day: 'numeric', month: 'long', year: 'numeric' });
}

function setDefaultBookingDate() {
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    const dateInput = document.getElementById('bookingDate');
    if (dateInput) {
        dateInput.min = tomorrow.toISOString().split('T')[0];
        dateInput.value = tomorrow.toISOString().split('T')[0];
    }
}

// ===== Scroll =====
function setupScrollListener() {
    const btn = document.getElementById('backToTop');
    const header = document.querySelector('.header');
    window.addEventListener('scroll', () => {
        btn.classList.toggle('visible', window.scrollY > 400);
        header.style.boxShadow = window.scrollY > 50 ? '0 4px 30px rgba(0,0,0,0.3)' : 'none';
    });
}

function scrollToTop() { window.scrollTo({ top: 0, behavior: 'smooth' }); }

// ===== Toast =====
function showToast(message, type = 'success') {
    const container = document.getElementById('toastContainer');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `${type === 'success' ? '✓' : '✕'} ${message}`;
    container.appendChild(toast);
    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateY(20px)';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// ===== Keyboard =====
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') { closeRestaurantModal(); closeEventModal(); }
    if (e.key === '/' && !e.ctrlKey && !e.metaKey) {
        const a = document.activeElement;
        if (a.tagName !== 'INPUT' && a.tagName !== 'TEXTAREA') { e.preventDefault(); toggleSearch(); }
    }
});
