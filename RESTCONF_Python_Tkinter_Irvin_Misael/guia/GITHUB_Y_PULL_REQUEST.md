# Entrega a GitHub: rama exacta `feat/unidad4_act02`

La rúbrica pide que la app `.py`, las capturas de GUI operando y el Pull Request estén en tu repositorio. Este ZIP es un proyecto local; **no crea un PR por sí mismo**.

## Repositorio existente

Copia la carpeta del laboratorio dentro de tu repositorio, o coloca sus archivos en la raíz si ese es el formato que pidió el profesor.

```bash
cd /ruta/a/tu/repositorio
git switch main                  # o la rama principal que use tu repositorio
git pull --ff-only
git switch -c feat/unidad4_act02
# Copia los archivos del ZIP y agrega capturas reales a evidencias/
git add .
git commit -m "feat: RESTCONF en Python y Tkinter - Irvin Misael Mejía Hernández"
git push -u origin feat/unidad4_act02
```

Si la rama ya existe, usa `git switch feat/unidad4_act02` en vez de crearla de nuevo. Si tu rama base no es `main`, sustituye ese nombre sin cambiar `feat/unidad4_act02`.

## Crear el Pull Request

- **Origen (head):** `feat/unidad4_act02`.
- **Destino (base):** `main` u otra rama principal indicada por el profesor.
- **Título recomendado:** `U4ACT02: Cliente RESTCONF con Python y Tkinter - Irvin Misael Mejía Hernández`.
- **Descripción:** copia el contenido de `.github/PULL_REQUEST_BODY.md`.
- **Evidencias:** agrega las capturas REALES de `evidencias/` antes de crear el PR.

Desde GitHub web: abre el repositorio → **Compare & pull request** para la rama enviada → revisa `base` y `compare` → pega la descripción y envía.

Opcional, si ya usas GitHub CLI:

```bash
gh pr create --base main --head feat/unidad4_act02 \
  --title "U4ACT02: Cliente RESTCONF con Python y Tkinter - Irvin Misael Mejía Hernández" \
  --body-file .github/PULL_REQUEST_BODY.md
```

**No subas usuario, contraseñas, tokens, información personal del sandbox ni archivos `.env`.**
