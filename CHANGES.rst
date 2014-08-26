=======
CHANGES
=======

-----
0.3.3
-----

- API CHANGE: now Stage.parse() is handled by Report.parse().
  Outcome behavior should remain the same
- Subclass SummaryStage from Stage.
  It can access normal stages' result_info in its result_info (#18)
- Add true functionality of Cufflinks page (#19)
- Fix py3.3 wheel dependencies
- Move change log before 0.3 to OLDCHANGES.rst

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

Older changes can be found in OLDCHANGES.rst
