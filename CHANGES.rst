=======
CHANGES
=======

-----
0.3.2
-----

- Add true functionality of Tophat page (#17)
- More unified result structure (#13, #14)
- Add doc for Tuxedo pipeline (#16)

-----
0.3.1
-----

- Add true funcionality of FastQC page (finally)
- Change templates' internal folder structure.
  Backward compatible but internal API has changed
  (e.g. _get_builtin_template_root -> _get_builtin_report_root)
- jQuery v2.1.1 now bundles in NGCloud
- Re-design frontend development (e.g. gulpfile.coffee)
- Improve Report.copy_static() function
- Make easier for external loggers embedded into ngreport
- Fix tuxedo template path priority and its block layout, CSS
- Fix result folder finding without digit prefix

---
0.3
---

- Use Gulp.js for frontend development (#11)
- No pathlib required during installation (#12)
- Add API for stage static file copying (#8)

-----
0.2.1
-----

- PDF doc by XeLaTex (#9)
- Doc update on extending builtin pipeline (#10)
- Add change log into doc
- Move repo to BioCloud-TW/ngcloud on GitHub

---
0.2
---

- No self.template_config() needed (#7)
- Rename Report.stage_template_cls to Report.stage_classnames

-----
0.1.1
-----

- Add Python 3.3 support
- Extensive doc update,
  add example to write a new pipeline from ground up

---
0.1
---

- Fix PyPI setting
- Update doc, add change log

-----
0.0.9
-----

- Initial release
