# 💎 UI/UX Pro Max Skill: High-Fidelity Engineering Standards

## 1. Adaptive Design DNA & Theme Awareness
- **Theme Determination**: Агент обязан в первую очередь определить текущую цветовую схему и дизайн-токены (Primary, Background, Accent) из `SPECIFICATION.md`.
- **No AI-Gradients**: Категорически запрещено использование типичных "ИИ-градиентов" (фиолетово-розовых). Используй чистые нейтральные или глубокие акцентные цвета.
- **Contrast & Accessibility**: Текст обязан соответствовать стандарту WCAG AA, обеспечивая идеальную читаемость на любом фоне.

## 2. Geometry & Spacing (The 8pt System)
- **Grid Discipline**: Все размеры, отступы (padding, margin) и зазоры (gap) должны быть строго кратны 8.
  - **Стандарты**: `p-2` (8px), `p-4` (16px), `gap-6` (24px).
- **Precision Engineering**: Избегай произвольных "магических" чисел (например, `h-[442px]`). Используй только системную сетку Tailwind.
- **Systemic Radius**: Закругление углов должно быть единообразным: `rounded-lg` (8px) для кнопок, `rounded-2xl` (16px) для карточек и модальных окон.

## 3. Typography: Information Architecture
- **Font Stack**: Приоритет — **Geist** (Vercel) или **Inter**. 
- **Data Integrity (Mono)**: Для любых технических данных, чисел, таймеров и финансовых показателей ВСЕГДА используй `font-mono`. Это предотвращает "дрожание" интерфейса при динамическом изменении значений.
- **Hierarchy Scale**:
  - **Display**: 24px+ (Bold, Tracking-tighter) — только для главных заголовков.
  - **Body**: 14px (Regular) — стандарт для большинства интерфейсных элементов.
  - **Caption**: 12px (Medium, Muted) — для второстепенных метаданных.
- **Leading**: Межстрочный интервал `leading-relaxed` для текста и `leading-none` для заголовков.

## 4. Interaction & Motion (The "Spring" Feel)
- **Framer Motion Only**: Линейные или стандартные CSS-анимации запрещены. Используй только физику пружин.
  - **Конфигурация**: `transition: { type: "spring", stiffness: 300, damping: 30 }`.
- **Micro-interactions**: 
  - **Visual Feedback**: Каждое нажатие кнопки обязано иметь отклик: `whileTap={{ scale: 0.98 }}`.
  - **Presence**: Используй `staggerChildren` для последовательного появления элементов списка с легким смещением по оси Y.
- **States**: Обязательная проработка всех интерактивных состояний: `:hover`, `:active`, `:focus-visible`, и `disabled`.

## 5. Layout Patterns & Logic
- **Component Logic**:
  - **Icons**: Только **Lucide React** или **svgl**. Толщина линий строго `stroke-width: 1.5`.
  - **Skeleton States**: Вместо спиннеров используй анимированные скелетоны, повторяющие форму контента.
  - **Empty States**: Пустые экраны должны содержать эстетичную иллюстрацию и четкий CTA-элемент.
- **Composition**:
  - **Sidebars**: Фиксированные (`sticky`) или скрываемые (`sheet`) с эффектом `backdrop-blur`.
  - **Terminal Pattern**: Для сложных систем управления обязателен NLP-ввод или командная строка (K-интерфейс) в нижней части экрана.

## 6. Delivery Checklist (AI Self-Review)
1. Проверена ли вся сетка на кратность 8?
2. Используется ли `font-mono` для всех числовых данных?
3. Соответствует ли цветовая палитра токенам из `SPECIFICATION.md`?
4. Добавлены ли пружинные анимации и `whileTap` отклик?
5. Проверена ли визуальная целостность через Playwright (скриншоты)?