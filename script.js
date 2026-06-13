/* ================================================
   script.js
   이 파일이 하는 일:
   1. 영어 명언 배열에서 랜덤으로 하나를 골라 표시
   2. data/weather.json  → 날씨 + 코디 카드 렌더링
   3. data/news.json     → 뉴스 카드 렌더링
   4. data/market.json   → 시장 지수 카드 렌더링
   5. data/supports.json → 지원사업 카드 렌더링
   ================================================ */

// ================================================
// 1. 영어 명언 데이터 (20개)
//    새 명언을 추가하려면 배열에 객체를 추가하면 됩니다.
// ================================================
const quotes = [
  { en: "The only way to do great work is to love what you do.", ko: "위대한 일을 하는 유일한 방법은 자신이 하는 일을 사랑하는 것이다.", author: "Steve Jobs" },
  { en: "In the middle of every difficulty lies opportunity.", ko: "모든 어려움 속에는 기회가 숨어 있다.", author: "Albert Einstein" },
  { en: "It does not matter how slowly you go as long as you do not stop.", ko: "멈추지 않는 한, 얼마나 천천히 가는지는 중요하지 않다.", author: "Confucius" },
  { en: "Life is what happens when you're busy making other plans.", ko: "삶이란 다른 계획을 세우느라 바쁜 동안 일어나는 것이다.", author: "John Lennon" },
  { en: "The future belongs to those who believe in the beauty of their dreams.", ko: "미래는 자신의 꿈이 아름답다고 믿는 사람들에게 속한다.", author: "Eleanor Roosevelt" },
  { en: "It always seems impossible until it's done.", ko: "무언가는 항상 완성되기 전까지는 불가능해 보인다.", author: "Nelson Mandela" },
  { en: "Success is not final, failure is not fatal: it is the courage to continue that counts.", ko: "성공이 끝이 아니고, 실패가 치명적인 것도 아니다. 중요한 것은 계속할 용기다.", author: "Winston Churchill" },
  { en: "Believe you can and you're halfway there.", ko: "할 수 있다고 믿는다면, 당신은 이미 절반은 온 것이다.", author: "Theodore Roosevelt" },
  { en: "The mind is everything. What you think you become.", ko: "마음이 전부다. 당신이 생각하는 것이 바로 당신이 된다.", author: "Buddha" },
  { en: "An unexamined life is not worth living.", ko: "성찰하지 않는 삶은 살 가치가 없다.", author: "Socrates" },
  { en: "Spread love everywhere you go. Let no one ever come to you without leaving happier.", ko: "가는 곳마다 사랑을 나눠라. 당신을 만난 사람이 더 행복해져서 떠나도록 하라.", author: "Mother Teresa" },
  { en: "When you reach the end of your rope, tie a knot in it and hang on.", ko: "밧줄 끝에 다다랐을 때, 매듭을 짓고 버텨라.", author: "Franklin D. Roosevelt" },
  { en: "Always remember that you are absolutely unique. Just like everyone else.", ko: "당신은 절대적으로 독특한 존재임을 항상 기억하라. 다른 모든 사람처럼.", author: "Margaret Mead" },
  { en: "Do not go where the path may lead, go instead where there is no path and leave a trail.", ko: "길이 이끄는 곳으로 가지 말고, 대신 길이 없는 곳으로 가서 흔적을 남겨라.", author: "Ralph Waldo Emerson" },
  { en: "You will face many defeats in life, but never let yourself be defeated.", ko: "인생에서 많은 패배를 맞이하겠지만, 스스로가 패배하는 일은 없도록 하라.", author: "Maya Angelou" },
  { en: "The greatest glory in living lies not in never falling, but in rising every time we fall.", ko: "삶에서 가장 큰 영광은 절대 넘어지지 않는 것이 아니라, 넘어질 때마다 다시 일어나는 것이다.", author: "Nelson Mandela" },
  { en: "In the end, it's not the years in your life that count. It's the life in your years.", ko: "결국 중요한 것은 당신 삶의 연수가 아니라, 그 연수 안에 담긴 삶이다.", author: "Abraham Lincoln" },
  { en: "Never let the fear of striking out keep you from playing the game.", ko: "삼진아웃에 대한 두려움이 게임을 포기하게 만들지 말라.", author: "Babe Ruth" },
  { en: "Life is either a daring adventure or nothing at all.", ko: "삶이란 대담한 모험이거나, 아무것도 아니다.", author: "Helen Keller" },
  { en: "You have brains in your head. You have feet in your shoes. You can steer yourself any direction you choose.", ko: "당신의 머릿속에는 두뇌가 있고, 신발 안에는 발이 있다. 당신이 선택하는 어느 방향으로든 나아갈 수 있다.", author: "Dr. Seuss" }
];

// ================================================
// 랜덤 명언 표시
// Math.random() 으로 0~19 사이 숫자를 뽑아 해당 명언을 보여줍니다.
// ================================================
function showRandomQuote() {
  const idx = Math.floor(Math.random() * quotes.length);
  const q = quotes[idx];
  document.getElementById('quote-en').textContent = q.en;
  document.getElementById('quote-ko').textContent = q.ko;
  document.getElementById('quote-author').textContent = q.author;
}

// ================================================
// 공통 fetch 헬퍼
// JSON 파일을 가져오고, 실패하면 null 을 반환합니다.
// 실패해도 페이지 전체가 깨지지 않도록 try-catch 로 감쌉니다.
// ================================================
async function fetchJSON(url) {
  try {
    const res = await fetch(url);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (e) {
    console.warn(`[fetchJSON] ${url} 로드 실패:`, e.message);
    return null;
  }
}

// 섹션 제목 옆에 업데이트 시각을 표시합니다.
function setUpdatedAt(sectionId, updatedAt) {
  if (!updatedAt) return;
  const section = document.getElementById(sectionId);
  if (!section) return;
  const title = section.querySelector('.section-title');
  if (!title) return;
  // 이미 추가된 경우 중복 방지
  if (title.querySelector('.updated-at')) return;
  const span = document.createElement('span');
  span.className = 'updated-at';
  span.textContent = `업데이트: ${updatedAt}`;
  title.appendChild(span);
}

// XSS 방지: 외부 데이터를 HTML 에 그대로 넣으면 위험하므로
// 특수문자를 안전하게 변환합니다.
function esc(str) {
  if (typeof str !== 'string') return '';
  return str
    .replace(/&/g, '&amp;').replace(/</g, '&lt;')
    .replace(/>/g, '&gt;').replace(/"/g, '&quot;').replace(/'/g, '&#39;');
}

// ================================================
// 섹션 1: 날씨 + 코디 렌더링
// data/weather.json 구조:
// { date, region, summary, temp_min, temp_max, rain, dust,
//   outfit_text, outfit_image_url, updated_at }
// ================================================
async function loadWeather() {
  const area = document.getElementById('weather-area');
  const data = await fetchJSON('./data/weather.json');

  if (!data) {
    area.innerHTML = '<p class="status-message">날씨 정보를 준비 중입니다. 잠시 후 다시 확인해 주세요.</p>';
    return;
  }

  // 무신사 코디맵 링크 (날씨 조건에 무관하게 연결)
  const munsinsaUrl = 'https://www.musinsa.com/app/codimap/lists';

  area.innerHTML = `
    <div class="weather-card">
      <div class="weather-info">
        <h3>📍 ${esc(data.region)} &nbsp; ${esc(data.date)}</h3>
        <div class="weather-row"><span>날씨</span><span>${esc(data.summary)}</span></div>
        <div class="weather-row"><span>기온</span><span>${esc(data.temp_min)}°C ~ ${esc(data.temp_max)}°C</span></div>
        <div class="weather-row"><span>강수</span><span>${esc(data.rain)}</span></div>
        <div class="weather-row"><span>미세먼지</span><span>${esc(data.dust)}</span></div>
      </div>
      <div class="outfit-info">
        <h3>👗 오늘의 추천 코디</h3>
        <p class="outfit-text">${esc(data.outfit_text)}</p>
        ${data.outfit_image_url
          ? `<img class="outfit-img" src="${esc(data.outfit_image_url)}" alt="코디 참고 이미지" onerror="this.style.display='none'" />`
          : ''}
        <a class="card-link" href="${munsinsaUrl}" target="_blank" rel="noopener">코디 더보기 →</a>
      </div>
    </div>
  `;

  setUpdatedAt('section-weather', data.updated_at);
  if (data.updated_at) {
    document.getElementById('footer-updated').textContent = `최종 업데이트: ${data.updated_at}`;
  }
}

// ================================================
// 섹션 2: 뉴스 카드 렌더링
// data/news.json 구조:
// { updated_at, items: [{ title, summary, source, date, link }] }
// ================================================
async function loadNews() {
  const area = document.getElementById('news-area');
  const data = await fetchJSON('./data/news.json');

  if (!data || !data.items || data.items.length === 0) {
    area.innerHTML = '<p class="status-message">뉴스 데이터를 준비 중입니다.</p>';
    return;
  }

  setUpdatedAt('section-news', data.updated_at);

  area.innerHTML = data.items.map(item => `
    <article class="card">
      <div class="card-meta">
        <span class="card-source">${esc(item.source)}</span>
        <span class="card-date">${esc(item.date)}</span>
      </div>
      <h3 class="card-title">${esc(item.title)}</h3>
      <p class="card-summary">${esc(item.summary)}</p>
      <a class="card-link" href="${esc(item.link)}" target="_blank" rel="noopener noreferrer">자세히 보기 →</a>
    </article>
  `).join('');
}

// ================================================
// 섹션 3: 시장 정보 렌더링
// data/market.json 구조:
// { updated_at, items: [{ name, value, change, change_pct, direction }] }
// direction: "up" | "down" | "flat"
// ================================================
async function loadMarket() {
  const area = document.getElementById('market-area');
  const data = await fetchJSON('./data/market.json');

  if (!data || !data.items || data.items.length === 0) {
    area.innerHTML = '<p class="status-message">시장 데이터를 준비 중입니다.</p>';
    return;
  }

  setUpdatedAt('section-market', data.updated_at);

  // 방향 기호
  const arrow = { up: '▲', down: '▼', flat: '─' };

  area.innerHTML = data.items.map(item => `
    <div class="market-card">
      <div class="market-name">${esc(item.name)}</div>
      <div class="market-value">${esc(item.value)}</div>
      <div class="market-change ${esc(item.direction)}">
        ${arrow[item.direction] || ''} ${esc(item.change)} (${esc(item.change_pct)})
      </div>
    </div>
  `).join('');
}

// ================================================
// 섹션 4: 지원사업 카드 렌더링
// data/supports.json 구조:
// { updated_at, items: [{ title, region, period, organization, summary, link }] }
// ================================================
async function loadSupports() {
  const area = document.getElementById('supports-area');
  const data = await fetchJSON('./data/supports.json');

  if (!data || !data.items || data.items.length === 0) {
    area.innerHTML = '<p class="status-message">지원사업 데이터를 준비 중입니다.</p>';
    return;
  }

  setUpdatedAt('section-supports', data.updated_at);

  area.innerHTML = data.items.map(item => `
    <article class="card">
      <div class="card-meta">
        <span class="card-tag">${esc(item.region)}</span>
        <span class="card-date">${esc(item.period)}</span>
      </div>
      <h3 class="card-title">${esc(item.title)}</h3>
      <p class="card-summary">
        <strong>${esc(item.organization)}</strong><br>
        ${esc(item.summary)}
      </p>
      <a class="card-link" href="${esc(item.link)}" target="_blank" rel="noopener noreferrer">공고 보기 →</a>
    </article>
  `).join('');
}

// ================================================
// 페이지 로드 시 모든 함수 실행
// ================================================
document.addEventListener('DOMContentLoaded', () => {
  showRandomQuote();   // 명언
  loadWeather();       // 날씨 + 코디
  loadNews();          // 뉴스
  loadMarket();        // 시장
  loadSupports();      // 지원사업
});
