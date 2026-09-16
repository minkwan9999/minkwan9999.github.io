import glob, os

SNIPPET = """
<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-Q543DWEBBW"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-Q543DWEBBW');
</script>
<!-- Google AdSense -->
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=pub-1957248819245044" crossorigin="anonymous"></script>
"""

for raw_path in glob.glob("**/raw.html", recursive=True):
    folder = os.path.dirname(raw_path)
    out_path = os.path.join(folder, "index.html")
    with open(raw_path, encoding="utf-8") as f:
        content = f.read()
    if "G-Q543DWEBBW" not in content:
        content = content.replace("</head>", SNIPPET + "\n</head>")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(content)
    print("Generated", out_path)
