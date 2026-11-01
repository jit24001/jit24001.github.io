# Jitendra Singh — editable academic website

This package preserves the current website's visual design and separate Home, Research, Publications, Projects, About, Hobbies and Connect pages. Text is kept in Markdown files. You do not need to edit HTML for routine updates.

## Publish on GitHub Pages

1. In your own browser, sign in to GitHub. For the short address `https://jit24001.github.io`, use a public repository named `jit24001.github.io`. If that repository already exists, review its current contents and make a backup before adding these files. For a different username, use `YOURUSERNAME.github.io`.
2. Extract the ZIP. Upload the contents of this folder into the repository's root on the `main` branch. Upload the folders and files, not the ZIP itself. The `README.md`, `site.yml`, `content`, `templates`, `assets` and `tools` should be at the repository root.
3. Include `.github/workflows/pages.yml`. It is essential for automatic publishing. On a Mac, press Command + Shift + . in Finder to show hidden folders before selecting files to upload. Check that `.github/workflows/pages.yml` is visible in the uploaded repository. If it was skipped, use Add file → Create new file on GitHub, enter `.github/workflows/pages.yml`, and paste the contents of the supplied file.
4. Open repository Settings → Pages. Under Source, choose GitHub Actions. Open Actions → Publish academic website → Run workflow if a deployment has not started. After the workflow succeeds, Settings → Pages shows the live URL.

The workflow uses GitHub's built-in repository token. You do not need to create or paste a personal access token, password or other secret.

The repository can also have another name, such as `academic-site`. Its URL will then normally include that project name. The build reads GitHub Pages settings and adjusts navigation, images and canonical URLs for that prefix automatically.

## Make an ordinary edit

1. Open the relevant file in GitHub and click the pencil icon.
2. Edit the text below the second `---` line, or change a labelled field in the header.
3. Click Commit changes and save to `main` (or merge your change into `main` if branch protection requires a pull request).
4. Wait for the Publish academic website workflow to succeed, then refresh your website.

| What to change | File |
| --- | --- |
| Email, name, affiliation, website address, education timeline | `site.yml` |
| Home introduction and tagline | `content/home.md` |
| Research page introduction | `content/research.md` |
| Each research topic | A file in `content/research/` |
| Publications page introduction | `content/publications.md` |
| Add or edit a paper | A file in `content/publications/` |
| Projects page introduction | `content/projects.md` |
| Add or edit a project | A file in `content/projects/` |
| About introduction | `content/about.md` |
| Hobbies and personal notes | `content/hobbies.md` |
| Connect page introduction and research note | `content/connect.md` |
| Design colours, font sizes and spacing | `assets/style.css` |

Markdown basics: `## A heading`, `**bold text**`, `- a list item`, and `[link text](https://example.com)`.

Settings between the two `---` lines use YAML. Keep the field names and indentation. When entering a title containing a colon, wrap it in quotation marks. Fields with `|` preserve line breaks. GitHub's Preview tab can help you inspect your Markdown before saving; the final website design is applied by the builder.

### Add a publication

Copy one file in `content/publications/`, give the copy a new filename, and edit its title, authors, year and venue. Put a publisher/PDF link in `link` if available. The paper and its year filter appear automatically. An optional paragraph below the header becomes a short summary.

### Add a project

Copy a file in `content/projects/`, choose a unique lowercase `id`, and edit its title, dates, role, tags and paragraphs. The `order` number controls position. New projects appear automatically; the existing project artwork is used only for its matching project id. Existing home-page cards for navigation and prosthetics use the `home_title` and `home_description` fields in those two project files.

### Add photographs

Upload a photo into `images/`, then add this to a content Markdown file:

```markdown
![A useful description of the image](/images/my-photo.jpg)
```

Images and files uploaded into this repository are public when published. The original CV PDF and its phone number have not been included in this package. The academic email displayed on the current site is included.

## Optional local preview

You need Python 3.10 or later. In this folder, run:

```bash
python3 -m pip install -r requirements.txt
python3 tools/build.py --site-url http://localhost:8000
python3 tools/check_links.py
python3 -m http.server 8000 --directory _site
```

Open `http://localhost:8000` in your browser. For a test build under a project subpath, supply the complete URL, such as `https://jit24001.github.io/academic-site`. Do not upload `_site` back into your source repository; it is generated automatically.

## Alternative hosting

The same source can be connected to Netlify using your own account. The supplied `netlify.toml` sets the build command and output folder. Editing is still done in the Markdown files. A form-based content editor such as Decap CMS can be added separately, but needs its own Git-provider authentication setup; it is not configured in this package.

## What is included

- The original responsive design, diagrams and mobile navigation.
- Seven separate page URLs.
- Publication search, year filters and citation-copy buttons.
- The interactive sequence-to-graph illustration.
- Markdown content files and a shared profile/timeline file.
- A GitHub Pages publishing workflow and link checks.

The Hobbies page intentionally says personal notes are coming soon until actual hobbies are supplied. The GitHub workflow has been prepared but has not yet run in your account.
