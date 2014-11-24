gulp = require 'gulp'
gutil = require 'gulp-util'
plumber = require 'gulp-plumber'  # robust error handler
stylus = require 'gulp-stylus'
nib = require 'nib'
coffee = require 'gulp-coffee'
del = require 'del'
rename = require 'gulp-rename'
gcolors = gutil.colors
path = require 'path'

releaseRoot = '../ngcloud/pipe/report/'
devRoot = './dev/'

paths =
    shared: './src/shared'
    tuxedo: './src/tuxedo'
    newqc: './src/newqc'

released = ['shared', 'tuxedo']

prettyLog = (err) ->
    gutil.log \
        gcolors.red('Error'),
        "from '#{gcolors.cyan err.plugin}'",
        "in #{gcolors.magenta file.path}",
        '\n          ',
        gcolors.red(err.name), gcolors.yellow(err.message),

compileCoffee = (pth, dest) ->
    gulp.src pth
        .on 'data', (file) ->           # to get the processing file
            gulp.src file.path          # restart the pipe
                .pipe plumber prettyLog # use plumber to handle error not to stop full task
                .pipe coffee
                    bare: true
                .pipe gulp.dest dest

compileStylus = (pth, dest, compress=false) ->
    gulp.src pth
        .on 'data', (file) ->
            gulp.src file.path
                .pipe plumber prettyLog
                .pipe stylus
                    compress: compress
                    use: [nib()]
                .pipe gulp.dest dest

gulp.task 'coffee', ->
    for subproj, subpath of paths
        compileCoffee pth=path.join(subpath, '*.coffee'),
            dest=path.join(devRoot, subproj, 'js')

gulp.task 'stylus', ->
    for subproj, subpath of paths
        compileStylus pth=(path.join subpath, '*.styl'),
            dest=path.join(devRoot, subproj, 'css')

gulp.task 'release', ->
    for subproj, subpath of paths when subproj in released
        gulp.src path.join(subpath, '*.coffee')
            .pipe coffee
                bare:true
            .on 'error', gutil.log
            .pipe gulp.dest path.join(releaseRoot, subproj, 'static', 'js')

        gulp.src path.join(subpath, '*.styl')
            .pipe stylus
                compress: true
                use: [nib()]
            .pipe gulp.dest path.join(releaseRoot, subproj, 'static', 'css'),

gulp.task 'clean', ->
    toClean = Array::concat (path.join devRoot, subproj, 'js/*.js' for subproj of paths),
        (path.join devRoot, subproj, 'css/*.css' for subproj of paths),
        (path.join releaseRoot, subproj, 'static', 'js/*.js' for subproj of paths when subproj in released),
        (path.join releaseRoot, subproj, 'static', 'css/*.css' for subproj of paths when subproj in released)
    del toClean

gulp.task 'default', ['coffee', 'stylus']
