# Missing YouTube IDs — 岡村孝子 Takako Okamura

Dataset: `src/data/discography.json` (the app reads this; `data/discography.json` is an identical legacy copy — ignore it).

**How to fill this in:** paste the 11-character video ID (from `watch?v=XXXXXXXXXXX`) into the last column of each row. Leave blank if you cannot find one.

**Valid URLs I can parse:** `https://www.youtube.com/watch?v=ID`, `https://youtu.be/ID`, or just the bare `ID`.


## 1. Singles missing a video (19)

Each row maps to a `singles[]` entry (has its own `youtubeId` field).

| # | Date | Title | youtubeId |
|---|------|-------|-----------|
| 1 | 1985-10-19 | 風は海から | https://youtu.be/UpJ_rIZOif8?list=RDUpJ_rIZOif8  |
| 2 | 1986-01-22 | 今日も眠れない | https://youtu.be/ppy_VmQ30H4  |
| 3 | 1986-07-23 | 夏の日の午後 | https://youtu.be/BbCivwkU8x4  |
| 4 | 1988-12-01 | クリスマスの夜 | https://youtu.be/c3VeXu-52cI  |
| 5 | 1989-07-01 | 青い風 | https://youtu.be/XqNumQGXeMo  |
| 6 | 1992-12-05 | 笑顔にはかなわない | https://youtu.be/BR20qg-ELFA  |
| 7 | 1993-06-09 | フォーエバー・ロマンス | https://youtu.be/ya2nSyGZRIA  |
| 8 | 1994-05-25 | ハレルヤ | https://youtu.be/AQ5Wmr1ZTVU  |
| 9 | 1994-08-24 | 山あり谷あり | https://youtu.be/TQl5kJPLKjo  |
| 10 | 1994-10-05 | ヒロイン 〜あの日の涙を忘れない〜 | https://www.youtube.com/watch?v=UQ9O7npH-i8&pp=ygVB44OS44Ot44Kk44OzIOOAnOOBguOBruaXpeOBrua2meOCkuW_mOOCjOOBquOBhOOAnCAgdGFrYWtvIG9rYW11cmE%3D  |
| 11 | 1994-10-05 | Naturally | https://www.youtube.com/watch?v=Kgft6nXBQyE&pp=ygUYTmF0dXJhbGx5IHRha2FrbyBva2FtdXJh |
| 12 | 1996-01-29 | Winter Story | https://youtu.be/wORu2f7tI44 |
| 13 | 1996-05-20 | いつも心に太陽を | https://youtu.be/jjzrUZtsczE |
| 14 | 1997-05-20 | 明日の幸せ | https://youtu.be/urfzs2Ut3eI |
| 15 | 2000-08-23 | 永遠の木もれ陽 | https://youtu.be/7FUHG3hdVLI |
| 16 | 2004-08-25 | 心のフレーム |https://www.youtube.com/watch?v=XI65ktoc_hc&pp=ygUh5b-D44Gu44OV44Os44O844OgIHRha2FrbyBva2FtdXJh  |
| 17 | 2005-01-26 | 春色のメロディー | https://youtu.be/Rj-5TdERAPw |
| 18 | 2010-12-04 | IDENTITY |https://youtu.be/9w2qODHzJz8  |
| 19 | 2019-04-24 | と・も・に (digital) | https://youtu.be/QdT5cqzViu4 |

## 2. Albums with NO playable track (9)

An album slide has no sample until at least one of its tracks gets a `youtubeId`. Paste an ID here and I will attach it to the first track of that album (you can also give me a specific track below).

| # | Date | Album | youtubeId (attach to first track) |
|---|------|-------|-----------------------------------|
| 1 | 1985-10-19 | 夢の樹 | https://youtu.be/bIIIXDPCGTQ |
| 2 | 1989-06-24 | Eau Du Ciel (天の水) | https://youtu.be/LL5AuUAi3gs |
| 3 | 1994-09-14 | SWEET HEARTS | https://youtu.be/kb_qmZE7TGA |
| 4 | 1996-02-19 | BRAND-NEW |https://youtu.be/ePSkFxwff9U  |
| 5 | 2000-08-23 | Reborn | https://www.youtube.com/watch?v=wP4kBmB4VBY&pp=ygUVUmVib3JuIHRha2FrbyBva2FtdXJh |
| 6 | 2005-03-23 | Sanctuary | https://www.youtube.com/watch?v=p1Bb5mcEYiU&pp=ygUYU2FuY3R1YXJ5IHRha2FrbyBva2FtdXJh |
| 7 | 2011-09-07 | 勇気 |https://www.youtube.com/watch?v=MRouqDoPpNA&pp=ygUV5YuH5rCXIHRha2FrbyBva2FtdXJh  |
| 8 | 2013-03-27 | NO RAIN, NO RAINBOW | https://www.youtube.com/watch?v=Ww6Lgh3x_7E&pp=ygUiTk8gUkFJTiwgTk8gUkFJTkJPVyB0YWtha28gb2thbXVyYQ%3D%3D |
| 9 | 2019-05-22 | fierte | https://www.youtube.com/watch?v=NgYsDNsdllg&pp=ygUVZmllcnRlIHRha2FrbyBva2FtdXJh |

## 3. All album tracks missing a video

Grouped by album. Fill any that you find.


### 1985-10-19 — 夢の樹  (9/9 tracks missing)

| # | Track | youtubeId |
|---|-------|-----------|
| 1 | 風は海から | https://www.youtube.com/watch?v=UpJ_rIZOif8&pp=ygUe6aKo44Gv5rW344GL44KJIHRha2FrbyBva2FtdXJh |
| 2 | 冷たい雨 |https://www.youtube.com/watch?v=xy5mEZO_MZg&pp=ygUb5Ya344Gf44GE6ZuoIHRha2FrbyBva2FtdXJh  |
| 3 | 一人息子 |https://youtu.be/KoMGrwCI_V4  |
| 4 | 見返してやるんだわ | https://www.youtube.com/watch?v=mGpkMrDHQYk&pp=ygUq6KaL6L-U44GX44Gm44KE44KL44KT44Gg44KPIHRha2FrbyBva2FtdXJh0gcJCSsMAYcqIYzv |
| 5 | 雨の街 |https://www.youtube.com/watch?v=4xz38Euu8WE&pp=ygUY6Zuo44Gu6KGXIHRha2FrbyBva2FtdXJh  |
| 6 | ピエロ | https://www.youtube.com/watch?v=DFdpISiC1jI&pp=ygUY44OU44Ko44OtIHRha2FrbyBva2FtdXJh |
| 7 | 煙草 | https://www.youtube.com/watch?v=k-jHQCUFDLE&pp=ygUV54WZ6I2JIHRha2FrbyBva2FtdXJh |
| 8 | 砕ける波に… | https://www.youtube.com/watch?v=KASER47wp9I&pp=ygUe56CV44GR44KL5rOi44GrIHRha2FrbyBva2FtdXJh |
| 9 | 夢の樹 | https://www.youtube.com/watch?v=J9ac2oBy0Bg&pp=ygUY5aSi44Gu5qi5IHRha2FrbyBva2FtdXJh |

### 1986-07-02 — 私の中の微風  (8/9 tracks missing)

| # | Track | youtubeId |
|---|-------|-----------|
| 1 | 見送るわ | https://www.youtube.com/watch?v=qhNoGzcbRE0&pp=ygUb6KaL6YCB44KL44KPIHRha2FrbyBva2FtdXJh |
| 2 | 微風 | https://www.youtube.com/watch?v=2LMFkJTYIWA&pp=ygUV5b6u6aKoIHRha2FrbyBva2FtdXJh |
| 3 | 美辞麗句 |https://www.youtube.com/watch?v=Af1Db9Gur4k&pp=ygUb576O6L6e6bqX5Y-lIHRha2FrbyBva2FtdXJh  |
| 4 | 夏の日の午後 | https://www.youtube.com/watch?v=c5BAuRKR68g&pp=ygUh5aSP44Gu5pel44Gu5Y2I5b6MIHRha2FrbyBva2FtdXJh |
| 5 | Baby,Baby | https://www.youtube.com/watch?v=ODtwvYsFK7c&pp=ygUYQmFieSxCYWJ5IHRha2FrbyBva2FtdXJh |
| 6 | ラスト・シーン | https://www.youtube.com/watch?v=MPV1xL1J7QM&pp=ygUk44Op44K544OI44O744K344O844OzIHRha2FrbyBva2FtdXJh |
| 7 | ひとりごと | https://www.youtube.com/watch?v=bZhJGgY7VAs&pp=ygUe44Gy44Go44KK44GU44GoIHRha2FrbyBva2FtdXJh |
| 8 | 今日も眠れない | https://www.youtube.com/watch?v=ppy_VmQ30H4&pp=ygUk5LuK5pel44KC55yg44KM44Gq44GEIHRha2FrbyBva2FtdXJh0gcJCSsMAYcqIYzv |

### 1987-07-05 — liberté  (6/9 tracks missing)

| # | Track | youtubeId |
|---|-------|-----------|
| 1 | リベルテ | https://www.youtube.com/watch?v=6ISznYYziHU&pp=ygUb44Oq44OZ44Or44OGIHRha2FrbyBva2FtdXJh |
| 2 | ついてない | https://www.youtube.com/watch?v=Y0iEOPj27pg&pp=ygUe44Gk44GE44Gm44Gq44GEIHRha2FrbyBva2FtdXJh0gcJCSsMAYcqIYzv |
| 3 | 五月の晴れた空 | https://www.youtube.com/watch?v=aM5kVopTNhQ&pp=ygUk5LqU5pyI44Gu5pm044KM44Gf56m6IHRha2FrbyBva2FtdXJh |
| 4 | 秋の日の夕暮れ | https://www.youtube.com/watch?v=n5Ohw9ofPdQ&pp=ygUk56eL44Gu5pel44Gu5aSV5pqu44KMIHRha2FrbyBva2FtdXJh |
| 5 | 私はここにいる | https://www.youtube.com/watch?v=bGezQY0lRFc&pp=ygUk56eB44Gv44GT44GT44Gr44GE44KLIHRha2FrbyBva2FtdXJh |
| 6 | 月が泣いた夜 | https://www.youtube.com/watch?v=Tq_xS1gk1R8&pp=ygUh5pyI44GM5rOj44GE44Gf5aScIHRha2FrbyBva2FtdXJh |

### 1988-07-01 — SOLEIL  (7/9 tracks missing)

| # | Track | youtubeId |
|---|-------|-----------|
| 1 | ドラマ | https://www.youtube.com/watch?v=iZUvVDG0hHQ&pp=ygUY44OJ44Op44OeIHRha2FrbyBva2FtdXJh |
| 2 | あなたと生きた季節 | https://www.youtube.com/watch?v=lbKpf3NRBOc&pp=ygUq44GC44Gq44Gf44Go55Sf44GN44Gf5a2j56-AIHRha2FrbyBva2FtdXJh |
| 3 | ソレイユ | https://www.youtube.com/watch?v=pawh2fridaA&pp=ygUb44K944Os44Kk44OmIHRha2FrbyBva2FtdXJh |
| 4 | クリスマスの夜 | https://www.youtube.com/watch?v=c3VeXu-52cI&pp=ygUk44Kv44Oq44K544Oe44K544Gu5aScIHRha2FrbyBva2FtdXJh |
| 5 | 輝き | https://www.youtube.com/watch?v=P3MaKt_xaQA&pp=ygUV6Lyd44GNIHRha2FrbyBva2FtdXJh |
| 6 | 私の空 | https://www.youtube.com/watch?v=M5ZylM_COyQ&pp=ygUY56eB44Gu56m6IHRha2FrbyBva2FtdXJh |
| 7 | 白い夏 | https://www.youtube.com/watch?v=Odr7FL8njQo&pp=ygUY55m944GE5aSPIHRha2FrbyBva2FtdXJh |

### 1989-06-24 — Eau Du Ciel (天の水)  (9/9 tracks missing)

| # | Track | youtubeId |
|---|-------|-----------|
| 1 | 長い時間 | https://www.youtube.com/watch?v=3oErOM0HuuA&pp=ygUb6ZW344GE5pmC6ZaTIHRha2FrbyBva2FtdXJh |
| 2 | 虹を追いかけて | https://www.youtube.com/watch?v=rbkwzhUc9RY&pp=ygUk6Jm544KS6L-944GE44GL44GR44GmIHRha2FrbyBva2FtdXJh |
| 3 | オー・ド・シエル (天の水) | https://www.youtube.com/watch?v=ejETLTv62a4&pp=ygUn44Kq44O844O744OJ44O744K344Ko44OrIHRha2FrbyBva2FtdXJh |
| 4 | それぞれの明日 | https://www.youtube.com/watch?v=o_3SOtBtPps&pp=ygUk44Gd44KM44Ge44KM44Gu5piO5pelIHRha2FrbyBva2FtdXJh |
| 5 | 愛を守りきれなくて | https://www.youtube.com/watch?v=ZOW_rs5JhwM&pp=ygUq5oSb44KS5a6I44KK44GN44KM44Gq44GP44GmIHRha2FrbyBva2FtdXJh |
| 6 | ジュ・テーム | https://www.youtube.com/watch?v=Pz8QtKTDeX0&pp=ygUh44K444Ol44O744OG44O844OgIHRha2FrbyBva2FtdXJh |
| 7 | 愛がほしい | https://www.youtube.com/watch?v=ceBaZgZ0W4c&pp=ygUe5oSb44GM44G744GX44GEIHRha2FrbyBva2FtdXJh |
| 8 | リフレイン |https://www.youtube.com/watch?v=OBC6T7VwP7s&pp=ygUd44Oq44OV44Os44Kk44OzdGFrYWtvIG9rYW11cmE%3D  |
| 9 | 青い風 | https://www.youtube.com/watch?v=XqNumQGXeMo&pp=ygUY6Z2S44GE6aKoIHRha2FrbyBva2FtdXJh |

### 1990-06-27 — Kiss 〜à côté de la mer〜  (7/9 tracks missing)

| # | Track | youtubeId |
|---|-------|-----------|
| 1 | 終わらない夏 |https://www.youtube.com/watch?v=CWmBbwgA928&pp=ygUh57WC44KP44KJ44Gq44GE5aSPIHRha2FrbyBva2FtdXJh0gcJCSsMAYcqIYzv  |
| 2 | Kiss | https://www.youtube.com/watch?v=MSrK3ipA6v4&pp=ygUTS2lzcyB0YWtha28gb2thbXVyYQ%3D%3D |
| 3 | 満ち潮 | https://www.youtube.com/watch?v=bI8ebUPO46k&pp=ygUY5rqA44Gh5r2uIHRha2FrbyBva2FtdXJh |
| 4 | 空の彼方まで | https://www.youtube.com/watch?v=oU7oHsNRAYU&pp=ygUg56m644Gu5b285pa544G-44GndGFrYWtvIG9rYW11cmE%3D |
| 5 | 青い日々 | https://www.youtube.com/watch?v=ZSw4dsskoXM&pp=ygUb6Z2S44GE5pel44CFIHRha2FrbyBva2FtdXJh |
| 6 | あの海へ今帰りたい 〜a cote de la mar〜 |https://www.youtube.com/watch?v=nVvXFHlcZyE&pp=ygUr44GC44Gu5rW344G45LuK5biw44KK44Gf44GEICB0YWtha28gb2thbXVyYQ%3D%3D  |
| 7 | adieu | https://www.youtube.com/watch?v=hDLD0NXVBmM&pp=ygUUYWRpZXUgdGFrYWtvIG9rYW11cmE%3D |

### 1991-07-17 — Chou-fleur  (8/9 tracks missing)

| # | Track | youtubeId |
|---|-------|-----------|
| 1 | もっと自由に | https://www.youtube.com/watch?v=fKouBYDe05c&pp=ygUh44KC44Gj44Go6Ieq55Sx44GrIHRha2FrbyBva2FtdXJh |
| 2 | 永遠の灯 | https://www.youtube.com/watch?v=yukNlc5j3AA&pp=ygUb5rC46YGg44Gu54GvIHRha2FrbyBva2FtdXJh |
| 3 | 愛を急がないで | https://www.youtube.com/watch?v=jt_DyhM8LHY&pp=ygUk5oSb44KS5oCl44GM44Gq44GE44GnIHRha2FrbyBva2FtdXJh |
| 4 | 白い世界 | https://www.youtube.com/watch?v=aBF7VILIxL0&pp=ygUb55m944GE5LiW55WMIHRha2FrbyBva2FtdXJh |
| 5 | ポプラ |https://www.youtube.com/watch?v=RJptGfGxPOA&pp=ygUX44Od44OX44OpdGFrYWtvIG9rYW11cmE%3D  |
| 6 | 恋の行方 | https://www.youtube.com/watch?v=hAnumwhidlQ&pp=ygUb5oGL44Gu6KGM5pa5IHRha2FrbyBva2FtdXJh |
| 7 | 宇宙の片すみ | https://www.youtube.com/watch?v=ZzMXt-Gf3Ik&pp=ygUh5a6H5a6Z44Gu54mH44GZ44G_IHRha2FrbyBva2FtdXJh |
| 8 | 新しいスタート | https://www.youtube.com/watch?v=zJUfJstpDq8&pp=ygUl5paw44GX44GE44K544K_44O844OIICB0YWtha28gb2thbXVyYQ%3D%3D |

### 1992-06-20 — mistral  (8/9 tracks missing)

| # | Track | youtubeId |
|---|-------|-----------|
| 1 | 移ろいゆく想い |https://www.youtube.com/watch?v=wHZqcTc3IMY&pp=ygUV56e744KN44GE44KG44GP5oOz44GE  |
| 2 | 昨日よりも、今日よりも | https://www.youtube.com/watch?v=DiiLpiBkZV0&pp=ygUh5pio5pel44KI44KK44KC44CB5LuK5pel44KI44KK44KC |
| 3 | Heartbreak | https://www.youtube.com/watch?v=YZB8deU2bnM&pp=ygUZSGVhcnRicmVhayB0YWtha28gb2thbXVyYQ%3D%3D |
| 4 | MARIAGE | https://www.youtube.com/watch?v=UEN-F50Ia-k&pp=ygUWTUFSSUFHRSB0YWtha28gb2thbXVyYQ%3D%3D |
| 5 | プロローグ |https://www.youtube.com/watch?v=FXj5osyuBIU&pp=ygUe44OX44Ot44Ot44O844KwIHRha2FrbyBva2FtdXJh  |
| 6 | 告白 | https://www.youtube.com/watch?v=8km85RM3mPw&pp=ygUV5ZGK55m9IHRha2FrbyBva2FtdXJh |
| 7 | さかまく未来 | https://www.youtube.com/watch?v=CK8Q6SkLTfk&pp=ygUh44GV44GL44G-44GP5pyq5p2lIHRha2FrbyBva2FtdXJh |
| 8 | ミッドナイト・ブルー | https://www.youtube.com/watch?v=Rlig_Tsoxkw&pp=ygUt44Of44OD44OJ44OK44Kk44OI44O744OW44Or44O8IHRha2FrbyBva2FtdXJh0gcJCSsMAYcqIYzv |

### 1993-07-28 — 満天の星  (8/9 tracks missing)

| # | Track | youtubeId |
|---|-------|-----------|
| 1 | 夢見る頃を過ぎても | https://youtu.be/yM8UFsN4E9Q |
| 2 | フォーエバー・ロマンス | https://youtu.be/OMK3h7WfRlU |
| 3 | 満天の星 | https://youtu.be/6tOt2ms0vPY |
| 4 | 夏のスピード | https://youtu.be/Ai0QuFGGc_o |
| 5 | ピリオド | https://youtu.be/pEFnW3udrWM |
| 6 | 星空はいつも | https://youtu.be/00R9vV-lc9g |
| 7 | 卒業 | https://youtu.be/YfUHPnJ9H8A |
| 8 | 笑顔にはかなわない | https://youtu.be/bWSPuVXuC6Q |

### 1994-09-14 — SWEET HEARTS  (10/10 tracks missing)

| # | Track | youtubeId |
|---|-------|-----------|
| 1 | 山あり谷あり | https://youtu.be/ypfa7ap8zlI |
| 2 | 明日への道 | https://youtu.be/kQj0uf2C2jg |
| 3 | ラビリンス | https://youtu.be/dGJvueyNTeE |
| 4 | Dear friend | https://youtu.be/8T4xyAmB79Q |
| 5 | Naturally | https://youtu.be/EhsGUR9SUzE |
| 6 | ハレルヤ | https://youtu.be/AQ5Wmr1ZTVU |
| 7 | 夢の途中 | https://youtu.be/Hgqys7OTO_Q |
| 8 | 海岸通り | https://youtu.be/RBBmPW-y1ps |
| 9 | あなたの隣り | https://youtu.be/-IFPV5FdvbU |
| 10 | Good-Day (Ballade Version) | https://youtu.be/CfakrDUaRGk |

### 1996-02-19 — BRAND-NEW  (10/10 tracks missing)

| # | Track | youtubeId |
|---|-------|-----------|
| 1 | Winter Story | https://youtu.be/wORu2f7tI44 |
| 2 | Single Life | https://youtu.be/__g3ZfEWSlM |
| 3 | オリジナルな二人 | https://youtu.be/5PMlw9pjGxk |
| 4 | 明日の風 | https://youtu.be/bHKLBmOhPbM |
| 5 | 思い出に変わる時 | https://youtu.be/aVH81JvredQ |
| 6 | ホームタウン | https://youtu.be/7X9KpYFCpD8 |
| 7 | Brand-new Days | https://youtu.be/ePSkFxwff9U |
| 8 | いつも心に太陽を | https://youtu.be/_mVF_kNH0Mo |
| 9 | 愛という名の翼 | https://youtu.be/vsqJzuoHkfA |
| 10 | ヒロイン (Album Version) |  |

### 2000-08-23 — Reborn  (9/9 tracks missing)

| # | Track | youtubeId |
|---|-------|-----------|
| 1 | Answer | https://youtu.be/AxwYSowHmzk |
| 2 | 永遠の木もれ陽 | https://youtu.be/irJk4gDASTc |
| 3 | 明日の幸せ (Version 2000) | https://youtu.be/urfzs2Ut3eI |
| 4 | 心のユートピア | https://youtu.be/4bpVp41yuEU |
| 5 | 白い夏 (Version 2000) | https://youtu.be/nbNt-Fe0QH0 |
| 6 | 砂塵にまぎれて | https://youtu.be/pfmRIel07XU |
| 7 | 山あり谷あり (Version 2000) | https://youtu.be/ypfa7ap8zlI |
| 8 | Reborn | https://youtu.be/wP4kBmB4VBY |
| 9 | Dearest Honey | https://youtu.be/l-FhMi_KR88 |

### 2003-09-25 — TEAR DROPS  (8/9 tracks missing)

| # | Track | youtubeId |
|---|-------|-----------|
| 1 | 真実の泉 | https://youtu.be/Mml76ApXpVQ |
| 2 | ゴンドワナの風 | https://youtu.be/R82aMibcCb4 |
| 3 | おかえり | https://youtu.be/30xHOo3aycc |
| 4 | あの夏の海 | https://youtu.be/yg_AAM1QcjE |
| 5 | Heaven knows | https://youtu.be/5sz0DJYYl7I |
| 6 | クリスマスの夜 (2003 Version) | https://youtu.be/r-pu6_gdh1w |
| 7 | 肩車 | https://youtu.be/i5c90RcC5ko |
| 8 | 涙のしずく | https://youtu.be/UQ9O7npH-i8 |

### 2005-03-23 — Sanctuary  (10/10 tracks missing)

| # | Track | youtubeId |
|---|-------|-----------|
| 1 | 青い月 | https://youtu.be/s_Ndq28jjuQ |
| 2 | 雨のクラクション | https://youtu.be/Q83CfbmAaqg |
| 3 | 1日 | https://youtu.be/pc5KB4KEHQI |
| 4 | looking for dream | https://youtu.be/DiDogc-8VlE |
| 5 | プラネタリウム | https://youtu.be/GAUKsuOd0_A |
| 6 | 希望の朝 | https://youtu.be/VhGMO8GIejw |
| 7 | 心のフレーム | https://youtu.be/XI65ktoc_hc |
| 8 | Lady | https://youtu.be/Lrdgl0UiTeU |
| 9 | 春色のメロディー | https://youtu.be/VEjpe5Q9cuo |
| 10 | 祈り | https://youtu.be/mgbln12D3wo |

### 2006-05-24 — 四つ葉のクローバー  (9/10 tracks missing)

| # | Track | youtubeId |
|---|-------|-----------|
| 1 | 四つ葉のクローバー | https://youtu.be/mwmZFOAXdts |
| 2 | 夢見る瞳 | https://youtu.be/UzcgRSEbnTo |
| 3 | Tomorrow | https://youtu.be/8e6Sm5KUDRg |
| 4 | 晩春 | https://youtu.be/83guEcChCZE |
| 5 | フックエンド・マナーの丘 | https://youtu.be/8K-nA_-JLpI |
| 6 | 以心伝心 | https://youtu.be/9b1nOC3btB8 |
| 7 | 聖域 〜sanctuary〜 | https://youtu.be/cbSTkE8pRNM |
| 8 | 暁の空 | https://youtu.be/7PKwioWw-80 |
| 9 | 永遠の夏 | https://youtu.be/kzif-AKUgLg |

### 2011-09-07 — 勇気  (10/10 tracks missing)

| # | Track | youtubeId |
|---|-------|-----------|
| 1 | 一期一会 〜ようこそ、私の庭へ〜 | https://youtu.be/zqdmAOlZoIQ |
| 2 | ずっと | https://youtu.be/HID3d6hPq2M |
| 3 | 勇気 〜courage〜 | https://youtu.be/MRouqDoPpNA |
| 4 | 雨上がりの虹のように | https://youtu.be/Lm406pyMBNY |
| 5 | IDENTITY | https://youtu.be/XH298krX4TY |
| 6 | 友よ 〜時のかなたへ〜 | https://youtu.be/WcOJQalEa-4 |
| 7 | どんどん | https://youtu.be/pNS0BlnkBdM |
| 8 | 星屑に願いを | https://youtu.be/MKy_i_YYbfc |
| 9 | mother | https://youtu.be/Ddl4EyiNM4Y |
| 10 | 夢をあきらめないで 2011 | https://youtu.be/TKa9sg0GJeA |

### 2013-03-27 — NO RAIN, NO RAINBOW  (10/10 tracks missing)

| # | Track | youtubeId |
|---|-------|-----------|
| 1 | あなたにめぐりあう旅 | https://youtu.be/QPz-JhNkwXM |
| 2 | ありがとう | https://youtu.be/tipEK5jNUV0 |
| 3 | 大切な人 | https://youtu.be/SXbEInYnEF4 |
| 4 | NO RAIN, NO RAINBOW | https://youtu.be/wBX4x6SWjqA |
| 5 | 運命なら… | https://youtu.be/_erGkeYodSQ |
| 6 | 時間の砂 2013 |  |
| 7 | あしたの歌 | https://youtu.be/qFYtU_b_WAw |
| 8 | ゴール | https://youtu.be/34CpziLGiUI |
| 9 | 青い風 2013 | https://youtu.be/PLdyRQtQuLA |
| 10 | ふるさとにて | https://youtu.be/K_RnpPciJ_M |

### 2019-05-22 — fierte  (9/9 tracks missing)

| # | Track | youtubeId |
|---|-------|-----------|
| 1 | 金色の陽ざし | https://youtu.be/x7_QsAAPplU |
| 2 | 君がいたあの夏 | https://youtu.be/ifB6VBujGOg |
| 3 | 遥かなる旅路 | https://youtu.be/gYRPjdN37GM |
| 4 | 永遠の灯 2019 | https://youtu.be/YMfTikkzm5Y |
| 5 | と・も・に | https://youtu.be/QdT5cqzViu4 |
| 6 | まっさらな朝 | https://youtu.be/U4JC7SjaWK0 |
| 7 | Hello (original version) | https://youtu.be/zCiz9zqhTEk |
| 8 | Answer 2019 | https://youtu.be/AxwYSowHmzk |
| 9 | happy song | https://youtu.be/bFfOgD9FiZM |

---

_Generated from the dataset. When you are done, hand this file back and I will write the IDs into `src/data/discography.json` and rebuild the deck._
