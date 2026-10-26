import re
from html.parser import HTMLParser

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

print("HTML size:", len(html), "bytes")

# Check required selectors and elements
checks = [
    ('data-theme="dark"', 'Default dark theme'),
    ('data-lang="zh"', 'Default zh language'),
    (':root[data-lang="en"] .zh { display: none !important; }', 'EN language rule'),
    (':root:not([data-lang="en"]) .en { display: none !important; }', 'ZH language rule'),
    (':root[data-theme="dark"]', 'Dark theme CSS variables'),
    (':root[data-theme="light"]', 'Light theme CSS variables'),
    ('id="langToggle"', 'Language toggle button'),
    ('id="themeToggle"', 'Theme toggle button'),
    ('id="stockCanvas"', 'Stock canvas chart'),
    ('id="comparisonTable"', 'Comparison matrix table'),
    ('id="episodesTable"', 'Streak episodes table'),
    ('2330', 'TSMC stock code'),
    ('2454', 'MediaTek stock code'),
    ('SP500', 'S&P 500 Index code'),
    ('SOX', 'PHLX Semiconductor Index code'),
    ('NASDAQ', 'Nasdaq Composite Index code'),
    ('DJI', 'Dow Jones Industrial Index code'),
    ('VT', 'Vanguard Total World ETF code'),
    ('VTI', 'Vanguard Total Stock Market ETF code'),
    ('BND', 'Vanguard Total Bond Market ETF code'),
    ('TSM', 'TSMC ADR code'),
    ('NVDA', 'NVIDIA stock code'),
    ('GOOGL', 'Google Alphabet stock code'),
    ('id="tabBtnStocks"', 'Stocks & TAIEX tab button'),
    ('id="tabBtnMacro"', 'Macro CPI & PMI tab button'),
    ('id="viewStocks"', 'Stocks tab view container'),
    ('id="viewMacro"', 'Macro CPI & PMI tab view container'),
    ('id="cpiCanvas"', 'CPI YoY% canvas chart'),
    ('id="pmiCanvas"', 'PMI Index canvas chart'),
    ('id="macroComparisonTable"', 'Macro CPI/PMI comparison matrix table'),
    ('id="macroHistoryTable"', 'Macro CPI/PMI monthly history table'),
]

for pattern, desc in checks:
    if pattern in html:
        print(f"[PASS] {desc}")
    else:
        print(f"[FAIL] Missing {desc}: {pattern}")

# Check HTML tag balance
class TagChecker(HTMLParser):
    def __init__(self):
        super().__init__()
        self.stack = []
        self.self_closing = {'meta', 'input', 'br', 'hr', 'img', 'link'}
        self.errors = []

    def handle_starttag(self, tag, attrs):
        if tag.lower() not in self.self_closing:
            self.stack.append(tag.lower())

    def handle_endtag(self, tag):
        t = tag.lower()
        if t in self.self_closing:
            return
        if not self.stack:
            self.errors.append(f"Unexpected closing tag </{t}> with empty stack")
        elif self.stack[-1] == t:
            self.stack.pop()
        else:
            self.errors.append(f"Mismatched tag: expected </{self.stack[-1]}>, got </{t}>")

checker = TagChecker()
checker.feed(html)
if checker.errors:
    print(f"[FAIL] Tag errors found ({len(checker.errors)}):", checker.errors[:5])
else:
    print(f"[PASS] HTML Tag balance verified cleanly! Remaining unclosed tags: {checker.stack}")

print("Validation completed.")
