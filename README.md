<!--
  Cards animados em SVG, desenhados por scripts/render_cards.py
  e atualizados todo dia por .github/workflows/update-profile-art.yml.
  O texto mora em profile.json. O retrato pontilhado mora em data/portrait.json.
  Não deixe linhas em branco neste bloco: o espaçamento já está dentro dos SVGs.
-->
<div align="center">
<a href="https://github.com/GeovaneVrs"><img src="./cards/hero.svg" width="100%" alt="Geovane Valerio. Inteligência artificial, dados e bancos. Ciência da Computação na UNINASSAU." /></a><br>
<img src="./cards/heatmap.svg" width="100%" alt="Gráfico de contribuições em azul, atualizado todo dia." /><br>
<img src="./cards/activity.svg" width="100%" alt="Contribuições dos últimos 12 meses, com a sequência e o dia mais cheio." /><br>
<a href="https://github.com/GeovaneVrs"><img src="./cards/ia.svg" width="33.333%" alt="IA. Modelos com Python e scikit-learn." /></a><a href="https://github.com/GeovaneVrs"><img src="./cards/dados.svg" width="33.333%" alt="Dados. Da fonte ao dado limpo." /></a><a href="https://github.com/GeovaneVrs"><img src="./cards/banco.svg" width="33.333%" alt="Banco. MySQL e o desenho das tabelas." /></a><br>
<img src="./cards/quote.svg" width="100%" alt="A paixão por tecnologia e o desejo de aprender são as chaves para o sucesso." />
</div>

<p align="center">
<a href="https://github.com/GeovaneVrs">GitHub</a> &nbsp;/&nbsp; <a href="https://www.linkedin.com/in/geovane-valerio-213175297/">LinkedIn</a>
</p>

<details>
<summary>Como atualizar os cards</summary>

O perfil é uma pilha de SVGs. O GitHub não executa CSS da página, então cada animação mora dentro da própria imagem. Para ver a prévia neste repositório:

```bash
npm install
npm run dev
```

Para mudar o texto, edite `profile.json` e rode:

```bash
python3 scripts/fetch_contributions.py
python3 scripts/render_cards.py
```

O retrato sai da foto pública do GitHub. Para refazê-lo: `python3 scripts/make_portrait.py`.

`STATIC=1 python3 scripts/render_cards.py` desenha o último quadro, sem movimento. A Action `.github/workflows/update-profile-art.yml` refaz o calendário e os cards todo dia.

Para este arquivo virar o perfil, o repositório no GitHub precisa se chamar `GeovaneVrs/GeovaneVrs`.

</details>
