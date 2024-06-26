import vapoursynth as vs
core = vs.core
clip = video_in.resize.Bicubic(format=vs.YUV420P8)
vden = 1000
vfps = container_fps*vden
dfps = display_fps*vden

# default is 400, less means interpolation will only happen when it will work well
ignore_threshold=400
# if n% of blocks change more than threshold then don't interpolate at all (default is 51%)
scene_change_percentage=100

if "video_in" in globals():
    # realtime
    clip = video_in
    # Needed because clip FPS is missing
    src_fps_num = int(container_fps * 1e8)
    src_fps_den = int(1e8)
    clip = core.std.AssumeFPS(clip, fpsnum=vfps, fpsden=vden)
else:
    # run with vspipe
    clip = core.ffms2.Source(source=in_filename)
    dfps=float(dfps)

# resolution in megapixels. 1080p ≈ 2MP, 720p ≈ 1MP
mpix = clip.width * clip.height / 1000000

# Skip interpolation for >FHD content due to performance constraints
if not mpix > 2.1:
    analParams = {
        'overlap': 0,
        'search': 3,
        'truemotion': True,    
    }
    blockParams = {
        'thscd1': ignore_threshold,
        'thscd2': int(scene_change_percentage*255/100),
        'mode': 1,
    }

# reduce motion interpolation quality for media exceeding HD
    if mpix > 0.9:
        analParams['search'] = 0
        blockParams['mode'] = 0
        quality = 'Low'
    else:
        quality = 'High'
    dfps_num = int(dfps * 1e4)
    dfps_den = int(1e4)
    print("[vapoursynth] {} quality motionflow interpolation: reflowing from {} fps to {} fps.".format(quality,vfps/vden,dfps/vden))
    super = core.mv.Super(clip, pel=2, sharp=2, rfilter=4)
    mvfw = core.mv.Analyse(super, blksize=32, isb=False, search=3, dct=5)
    mvbw = core.mv.Analyse(super, blksize=32, isb=True,  search=3, dct=5)
    clip = core.mv.FlowFPS(clip, super, mvbw, mvfw, num=dfps, den=vden, mask=1)
clip.set_output()
