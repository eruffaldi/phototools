import os
import sys
import subprocess
from myexif import getexif
from PIL import Image,ImageFont,ImageDraw
from compmake import Context

class mytool:
    def __init__(self):
        self.c = Context()
        self.count = 0
        self.copied_file = [] #['./in001.png', './in002.png']
        self.slideshow_list_filename = 'xSofia.txt'

    def get_iframes(self, video):
        #ffmpeg -i yosemiteA.mp4 -f image2 -vf "select='eq(pict_type,PICT_TYPE_I)'" -vsync vfr yi%03d.png
        cmd = ['ffmpeg','-i', video,'-f', 'image2','-vf', 
               "select='eq(pict_type,PICT_TYPE_I)'",'-vsync','vfr','yi%03d.png']
        subprocess.call(cmd)

    def add_fade_effect(self, infilename, outfilename = 'final'):
        # Makes two frames : at the beginning and at the end
        # This is done by copying one I-Frame for a slide
        # Then, adds fades at both ends
 
        # make normal slide
        # ffmpeg -r 1/5 -i in%03d.png -c:v libx264 -r 30 -y -pix_fmt yuv420p slide.mp4 
        in_framerate = 1./5
        out_framerate = 30
        frames = 10 # seconds
        cmd = ['ffmpeg', '-loop',1,'-r', in_framerate, '-i',infilename,'-c:v','libx264', '-t',frames,
              '-r', out_framerate, '-y','-pix_fmt','yuv420p','slide.mp4'] 
        cmd = map(lambda x: '%s' %x, cmd)
        subprocess.call(cmd)

        # add fade-in effect - from 0th to 30th frame
        #ffmpeg -i slide.mp4 -y -vf fade=in:0:30 slide_fade_in.mp4
        cmd = ['ffmpeg', '-i','slide.mp4','-y','-vf','fade=in:0:30','slide_fade_in.mp4']
        subprocess.call(cmd)

        # add fade-out effect to the slide that has fade-in effect already : 30 frames starting from 120th  
        #ffmpeg -i slide_fade_in.mp4 -y -vf fade=out:120:30 slide_fade_in_out.mp4 
        cmd = ['ffmpeg', '-i','slide_fade_in.mp4','-y','-vf','fade=out:120:30', 'slide_fade_in_out.mp4'] 
        subprocess.call(cmd)

        # rename the output to 'final#.mp4'
        slide_name = outfilename
        cmd = map(lambda x: '%s' %x, ['mv', 'slide_fade_in_out.mp4', slide_name]) 
        print cmd
        subprocess.call(cmd)
 
        return slide_name
 
    # make concat list
    def make_slideshow_list(self, slides, fname='mylist.txt'):
        self.slideshow_list_filename = fname
        with open(self.slideshow_list_filename, mode='wb') as f:
            for slide in slides:
                f.write('file ' + slide +'\n')

    # concat all slides in the slideshow list
    def concat_slides(self, slideshow_name ,slideshow_list_filename ):
        cmd = ['ffmpeg', '-y', '-f','concat','-i', slideshow_list_filename, '-c', 'copy', slideshow_name] 
        subprocess.call(cmd)

    # get the list of file 
    def file_list(self, d, name):
        slides = []
        for x in open(name,"r"):
            id,date,text = x.strip().split(" ",2)
            text = text.decode("UTF-8")
            filename = "IMG_%s.JPG" % id
            fp = os.path.join(d,filename)
            tags = getexif(fp)
            slides.append(dict(id=id,filename=filename,fp=fp,date=date,text=text,width=tags["width"],height=tags["height"]))
        return slides

def makebackground(s,centered,outsize,path):
    img_w, img_h = centered.size # same as 
    background = Image.new('RGBA', (outsize[0], outsize[1]), (255, 255, 255, 255))
    bg_w, bg_h = outsizeimage # and not outsize
    offset = ((bg_w - img_w) / 2, (bg_h - img_h) / 2)
    draw = ImageDraw.Draw(background)
    text = "%s: %s" % (s["date"],s["text"])
    w,h = draw.textsize(text,font=font)
    if w > outsize[0] or h > textheight:
        print "TOO BIG", w,h
        sys.exit(0)
    draw.text(((outsize[0]-w)/2,outsizeimage[1]+(textheight-h)/2),text,(0,0,0),font=font)
    background.paste(img, offset)
    background.save(c)
    print "adjusted",s["filename"]
    return background

def makecentered(s,outsizeimage,path):
    c = os.path.join(path,"centered","%d_%s" % (s["count"],s["filename"]))
    #if not os.path.isfile(c):
    #if s["width"] != outsize[0] or s["height"] != outsize[1]:
    img = Image.open(s["fp"],"r")
    img_w, img_h = img.size # same as 
    if s["width"] > outsizeimage[0] or s["height"] > outsizeimage[1]:
        print "stretch to fit",s
        ratio = img_w/float(img_h)
        if s["width"] > outsizeimage[0]:
            sz = (outsizeimage[0],int(outsizeimage[0]/ratio))
        else:
            sz = (int(outsizeimage[1]*ratio),outsizeimage[1])
        img = img.resize(sz, Image.ANTIALIAS)
    return img

def makefaded(s,centered,faded,path):
    c = os.path.join(path,"fade","%d_%s.mp4" % (s["count"],s["id"]))
    s["faded"] = c
    if not os.path.isfile(c):
    print "making",c
    m.add_fade_effect(s["centered"], c)
    #    outlist.append("file %d_%s.mp4" % (s["count"],s["id"]))

def makefinal(allfaded,m,slideshow_name,listname):
    m.concat_slides(slideshow_name,listname)

if __name__ == '__main__':


    m = mytool()

    if len(sys.argv) <= 1:
        path = '.'
    elif len(sys.argv) == 2:
        path = sys.argv[1]
    else:
        path = sys.argv[1]
        video_name = sys.argv[2]
        # extract i-frames
        #m.get_iframes(video_name)


    #frame outputsize
    outsize = [1920,1080]
    textheight = 200
    outsizeimage = [outsize[0],outsize[1]-textheight]
    font = ImageFont.truetype("/Users/eruffaldi/Library/Fonts/Hack-Regular.ttf", 36)

    # get list of slide files (i-frames)
    slides = m.file_list(os.path.join(path,"original"),"xSofia.txt")
    for count,s in enumerate(slides):
        s["count"] = count
        s["centered"] = m.c.comp(makecentered,s,outsizeimage,path)
        s["background"] = m.c.comp(makebackground,s,s["centered"],outsize,path)

    fade_slides = []
    outfile_name = 'yos'
    outlist = []
    allfaded = []
    for s in slides:
        s["faded"] = m.c.comp(makefaded,s["centered"],s["background"],path)
        outlist.append("file %d_%s.mp4" % (s["count"],s["id"]))
        allfaded.append(s["faded"])
    
    # OK this is anyway
    listname = 'fade/slideshow_list.txt'
    of = open(listname,"wt")
    of.write("\n".join(outlist))
    of.close()

    # concatenate the slides in the list file
    m.c.comp(makefinal,m,allfaded,'yosemite_with_fades.mp4',listname)

    cmds = sys.argv[1:]
    if cmds:
        m.c.batch_command(' '.join(cmds))
    else:
        print('Use "make recurse=1" or "parmake recurse=1" to make all.')
        m.c.compmake_console()
