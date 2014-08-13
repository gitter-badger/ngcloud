gulp = require 'gulp'
gutil = require 'gulp-util'
plumber = require 'gulp-plumber'  # robust error handler
stylus = require 'gulp-stylus'
coffee = require 'gulp-coffee'
gcolors = gutil.colors

paths =
    coffee: ['./src/**/*.coffee']
    stylus: ['./src/**/*.styl']

gulp.task 'coffee', ->
    gulp.src paths.coffee
        .on 'data', (file) ->           # to get the processing file
            gulp.src file.path          # restart the pipe
                .pipe plumber (err) ->  # use plumber to handle error not to stop full task
                    gutil.log \
                        gcolors.red('Error'),
                        "from '#{gcolors.cyan err.plugin}'",
                        "in #{gcolors.magenta file.path}",
                        '\n          ',
                        gcolors.red(err.name), gcolors.yellow(err.message),
                .pipe coffee bare: true
                .pipe gulp.dest './js'

nib = require 'nib'
gulp.task 'stylus', ->
    gulp.src paths.stylus
        .on 'data', (file) ->
            gulp.src file.path
                .pipe plumber (err) ->
                    gutil.log \
                        gcolors.red('Error'),
                        "from '#{gcolors.cyan err.plugin}'",
                        "in #{gcolors.magenta file.path}",
                        '\n          ',
                        gcolors.red(err.name), gcolors.yellow(err.message),
                .pipe stylus
                    compress: true
                    use: [nib()]
                .pipe gulp.dest './css'

gulp.task 'watch', ->
    gulp.watch paths.coffee, ['coffee']
    gulp.watch paths.stylus, ['stylus']

gulp.task 'release', ->
    releaseDest = '../ngcloud/pipe/report/static/'
    gulp.src paths.coffee
        .pipe coffee
            bare: true
        .on 'error', gutil.log
        .pipe gulp.dest releaseDest + 'js'

    gulp.src paths.stylus
        .pipe stylus
            compress: true
            use: [nib()]
        .pipe gulp.dest releaseDest + 'css'


gulp.task 'default', ['coffee', 'stylus']
