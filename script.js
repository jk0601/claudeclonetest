// ==========================================
// 영어 명언 데이터
// 새 명언을 추가하려면 이 배열에 객체를 추가하면 됩니다.
// ==========================================
const quotes = [
  {
    en: "The only way to do great work is to love what you do.",
    ko: "위대한 일을 하는 유일한 방법은 자신이 하는 일을 사랑하는 것이다.",
    author: "Steve Jobs"
  },
  {
    en: "In the middle of every difficulty lies opportunity.",
    ko: "모든 어려움 속에는 기회가 숨어 있다.",
    author: "Albert Einstein"
  },
  {
    en: "It does not matter how slowly you go as long as you do not stop.",
    ko: "멈추지 않는 한, 얼마나 천천히 가는지는 중요하지 않다.",
    author: "Confucius"
  },
  {
    en: "Life is what happens when you're busy making other plans.",
    ko: "삶이란 다른 계획을 세우느라 바쁜 동안 일어나는 것이다.",
    author: "John Lennon"
  },
  {
    en: "The future belongs to those who believe in the beauty of their dreams.",
    ko: "미래는 자신의 꿈이 아름답다고 믿는 사람들에게 속한다.",
    author: "Eleanor Roosevelt"
  },
  {
    en: "It always seems impossible until it's done.",
    ko: "무언가는 항상 완성되기 전까지는 불가능해 보인다.",
    author: "Nelson Mandela"
  },
  {
    en: "Success is not final, failure is not fatal: it is the courage to continue that counts.",
    ko: "성공이 끝이 아니고, 실패가 치명적인 것도 아니다. 중요한 것은 계속할 용기다.",
    author: "Winston Churchill"
  },
  {
    en: "Believe you can and you're halfway there.",
    ko: "할 수 있다고 믿는다면, 당신은 이미 절반은 온 것이다.",
    author: "Theodore Roosevelt"
  },
  {
    en: "The mind is everything. What you think you become.",
    ko: "마음이 전부다. 당신이 생각하는 것이 바로 당신이 된다.",
    author: "Buddha"
  },
  {
    en: "An unexamined life is not worth living.",
    ko: "성찰하지 않는 삶은 살 가치가 없다.",
    author: "Socrates"
  },
  {
    en: "Spread love everywhere you go. Let no one ever come to you without leaving happier.",
    ko: "가는 곳마다 사랑을 나눠라. 당신을 만난 사람이 더 행복해져서 떠나도록 하라.",
    author: "Mother Teresa"
  },
  {
    en: "When you reach the end of your rope, tie a knot in it and hang on.",
    ko: "밧줄 끝에 다다랐을 때, 매듭을 짓고 버텨라.",
    author: "Franklin D. Roosevelt"
  },
  {
    en: "Always remember that you are absolutely unique. Just like everyone else.",
    ko: "당신은 절대적으로 독특한 존재임을 항상 기억하라. 다른 모든 사람처럼.",
    author: "Margaret Mead"
  },
  {
    en: "Do not go where the path may lead, go instead where there is no path and leave a trail.",
    ko: "길이 이끄는 곳으로 가지 말고, 대신 길이 없는 곳으로 가서 흔적을 남겨라.",
    author: "Ralph Waldo Emerson"
  },
  {
    en: "You will face many defeats in life, but never let yourself be defeated.",
    ko: "인생에서 많은 패배를 맞이하겠지만, 스스로가 패배하는 일은 없도록 하라.",
    author: "Maya Angelou"
  },
  {
    en: "The greatest glory in living lies not in never falling, but in rising every time we fall.",
    ko: "삶에서 가장 큰 영광은 절대 넘어지지 않는 것이 아니라, 넘어질 때마다 다시 일어나는 것이다.",
    author: "Nelson Mandela"
  },
  {
    en: "In the end, it's not the years in your life that count. It's the life in your years.",
    ko: "결국 중요한 것은 당신 삶의 연수가 아니라, 그 연수 안에 담긴 삶이다.",
    author: "Abraham Lincoln"
  },
  {
    en: "Never let the fear of striking out keep you from playing the game.",
    ko: "삼진아웃에 대한 두려움이 게임을 포기하게 만들지 말라.",
    author: "Babe Ruth"
  },
  {
    en: "Life is either a daring adventure or nothing at all.",
    ko: "삶이란 대담한 모험이거나, 아무것도 아니다.",
    author: "Helen Keller"
  },
  {
    en: "You have brains in your head. You have feet in your shoes. You can steer yourself any direction you choose.",
    ko: "당신의 머릿속에는 두뇌가 있고, 신발 안에는 발이 있다. 당신이 선택하는 어느 방향으로든 나아갈 수 있다.",
    author: "Dr. Seuss"
  }
];

// ==========================================
// 랜덤 명언 표시 함수
// ==========================================
function showRandomQuote() {
  // 0 ~ (quotes.length - 1) 범위의 랜덤 숫자를 뽑습니다.
  const randomIndex = Math.floor(Math.random() * quotes.length);
  const quote = quotes[randomIndex];

  // HTML 요소에 명언 내용을 넣습니다.
  document.getElementById('quote-en').textContent = quote.en;
  document.getElementById('quote-ko').textContent = quote.ko;
  document.getElementById('quote-author').textContent = quote.author;
}

// ==========================================
// 콘텐츠 카드 생성 함수
// data/contents.json 파일에서 데이터를 읽어와 카드를 만듭니다.
// ==========================================
async function loadContents() {
  try {
    // JSON 파일을 가져옵니다 (fetch API 사용)
    const response = await fetch('./data/contents.json');

    // 파일을 가져오지 못한 경우 에러 처리
    if (!response.ok) {
      throw new Error('데이터를 불러오지 못했습니다.');
    }

    const data = await response.json();

    // 업데이트 날짜 표시
    const updateEl = document.getElementById('last-updated');
    if (updateEl && data.lastUpdated) {
      updateEl.textContent = `최종 업데이트: ${data.lastUpdated}`;
    }

    // 각 섹션을 순서대로 화면에 그립니다.
    data.sections.forEach(section => renderSection(section));

  } catch (error) {
    // 에러가 발생하면 사용자에게 안내 메시지를 표시합니다.
    console.error('콘텐츠 로드 오류:', error);
    document.getElementById('content-area').innerHTML =
      '<p class="status-message">콘텐츠를 불러오는 중 오류가 발생했습니다. 잠시 후 다시 시도해 주세요.</p>';
  }
}

// ==========================================
// 섹션(카드 묶음) 하나를 화면에 그리는 함수
// ==========================================
function renderSection(section) {
  const container = document.getElementById('content-area');

  // 섹션 전체를 감싸는 div 생성
  const sectionEl = document.createElement('div');
  sectionEl.className = 'content-section';

  // 섹션 제목
  const titleEl = document.createElement('h2');
  titleEl.className = 'section-title';
  titleEl.textContent = section.title;
  sectionEl.appendChild(titleEl);

  // 카드를 담는 그리드
  const gridEl = document.createElement('div');
  gridEl.className = 'card-grid';

  // 각 아이템을 카드로 만들어 그리드에 추가
  section.items.forEach(item => {
    gridEl.appendChild(createCard(item));
  });

  sectionEl.appendChild(gridEl);
  container.appendChild(sectionEl);
}

// ==========================================
// 카드 HTML 요소를 만들어 반환하는 함수
// ==========================================
function createCard(item) {
  const card = document.createElement('article');
  card.className = 'card';

  // 카드 내용을 HTML로 작성
  card.innerHTML = `
    <div class="card-meta">
      <span class="card-tag">${escapeHtml(item.tag)}</span>
      <span class="card-date">${escapeHtml(item.date)}</span>
    </div>
    <h3 class="card-title">${escapeHtml(item.title)}</h3>
    <p class="card-summary">${escapeHtml(item.summary)}</p>
    <a class="card-link" href="${escapeHtml(item.link)}" target="_blank" rel="noopener noreferrer">
      자세히 보기 →
    </a>
  `;

  return card;
}

// ==========================================
// XSS 방지용 HTML 이스케이프 함수
// 사용자 데이터를 그대로 innerHTML에 넣으면 보안 위험이 생기므로
// 특수문자를 안전하게 변환합니다.
// ==========================================
function escapeHtml(str) {
  if (typeof str !== 'string') return '';
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

// ==========================================
// 페이지가 로드되면 실행
// ==========================================
document.addEventListener('DOMContentLoaded', () => {
  showRandomQuote();   // 랜덤 명언 표시
  loadContents();      // 콘텐츠 카드 로드
});
