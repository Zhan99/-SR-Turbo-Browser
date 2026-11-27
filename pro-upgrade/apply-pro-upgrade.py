#!/usr/bin/env python3
"""Apply the isolated SR Turbo Pro upgrade to the extracted source ZIP."""
from pathlib import Path
import sys

root = Path(sys.argv[1]).resolve()
activity = root / "app/src/main/java/com/srcreation/browser/BrowserActivity.java"
gradle = root / "app/build.gradle"
if not activity.is_file() or not gradle.is_file():
    raise SystemExit("Android project files not found; refusing partial patch.")

source = activity.read_text(encoding="utf-8")
anchor = '    void settings(){showControlCenter(true);}\n'
if source.count(anchor) != 1:
    raise SystemExit("BrowserActivity settings anchor mismatch; no Java changes applied.")

methods = r'''    void settings(){showControlCenter(true);}
    /** Live overview of the browser's existing features; this does not replace any core screen. */
    void proDashboard(){
        Dialog dialog=new Dialog(this);dialog.requestWindowFeature(Window.FEATURE_NO_TITLE);
        LinearLayout shell=Ui.column(this);Ui.pad(shell,this,18);shell.setBackground(Ui.bg(paper(),24,this));
        LinearLayout heading=Ui.row(this);LinearLayout titles=Ui.column(this);
        titles.addView(Ui.text(this,"SR TURBO PRO",22,fg(),true));
        titles.addView(Ui.text(this,"BROWSER PERFORMANCE CENTER",10,accent(),true));
        heading.addView(titles,new LinearLayout.LayoutParams(0,-2,1));
        heading.addView(Ui.button(this,"×",fg(),card(),dialog::dismiss));shell.addView(heading);
        TextView intro=Ui.text(this,"Your browser at a glance. All existing browsing, privacy and download tools remain available.",12,muted(),false);
        intro.setPadding(0,Ui.dp(this,8),0,Ui.dp(this,12));shell.addView(intro);
        ScrollView scroll=new ScrollView(this);LinearLayout body=Ui.column(this);scroll.addView(body);
        LinearLayout row1=Ui.row(this);row1.setGravity(Gravity.TOP);
        dashboardMetric(row1,"OPEN TABS",tabs.size()+" / 20");
        dashboardMetric(row1,"CONNECTIONS",String.valueOf(connections));
        body.addView(row1);
        LinearLayout row2=Ui.row(this);row2.setGravity(Gravity.TOP);
        dashboardMetric(row2,"BOOKMARKS",privateMode()?"PRIVATE":String.valueOf(bookmarks.size()));
        dashboardMetric(row2,"HISTORY",privateMode()?"PRIVATE":String.valueOf(history.size()));
        body.addView(row2);
        DownloadBadge meter=new DownloadBadge();
        if(!privateMode()){
            synchronized(DownloadService.class){DownloadService.load(this);for(DownloadService.Task task:DownloadService.tasks.values())meter.add(task.state,task.bytes,task.total);}
            if(meter.count==0&&YouTubeDownloadService.busy&&!"Updating".equals(YouTubeDownloadService.state))meter.video(YouTubeDownloadService.state,YouTubeDownloadService.bytes,YouTubeDownloadService.total);
        }
        section(body,"DOWNLOAD ACTIVITY");
        body.addView(Ui.text(this,meter.count==0?"No active downloads":meter.description(),13,fg(),true));
        body.addView(Ui.text(this,"Turbo Boost: "+(turbo()?"ON":"OFF")+"  •  Up to "+connections+" connections",12,muted(),false));
        section(body,"PROTECTION & APPEARANCE");
        body.addView(Ui.text(this,"Blocked requests: "+blockedRequests.get()+"  •  Pop-ups: "+blockedPopups.get()+"  •  Video skip actions: "+skippedAds.get(),12,fg(),false));
        body.addView(Ui.text(this,"Theme: "+theme.title+"  •  Display: "+displayMode.title+"  •  Ad protection: "+(adProtection!=null&&adProtection.any(active()==null?"":active().url)?"ON":"READY"),12,muted(),false));
        section(body,"QUICK ACTIONS");
        LinearLayout actions=Ui.row(this);actions.setPadding(0,Ui.dp(this,6),0,0);
        TextView downloads=Ui.button(this,"↓  Downloads",fg(),card(),()->{dialog.dismiss();downloads();});
        TextView themes=Ui.button(this,"✦  Themes",fg(),card(),()->{dialog.dismiss();ThemeGallery.show(this);});
        actions.addView(downloads,new LinearLayout.LayoutParams(0,-2,1));actions.addView(themes,new LinearLayout.LayoutParams(0,-2,1));body.addView(actions);
        LinearLayout actions2=Ui.row(this);actions2.setPadding(0,Ui.dp(this,7),0,0);
        TextView settings=Ui.button(this,"⚙  Settings",fg(),card(),()->{dialog.dismiss();settings();});
        TextView protection=Ui.button(this,"⬟  Protection",fg(),card(),()->{dialog.dismiss();adSettings();});
        actions2.addView(settings,new LinearLayout.LayoutParams(0,-2,1));actions2.addView(protection,new LinearLayout.LayoutParams(0,-2,1));body.addView(actions2);
        shell.addView(scroll,new LinearLayout.LayoutParams(-1,0,1));
        shell.addView(Ui.button(this,"Done",Color.WHITE,palette().nav,dialog::dismiss));
        dialog.setContentView(shell);dialog.show();Window window=dialog.getWindow();if(window!=null){window.setBackgroundDrawableResource(android.R.color.transparent);window.setLayout(Math.min(getResources().getDisplayMetrics().widthPixels-Ui.dp(this,28),Ui.dp(this,440)),Math.min(getResources().getDisplayMetrics().heightPixels-Ui.dp(this,80),Ui.dp(this,680)));}
    }
    void dashboardMetric(LinearLayout host,String label,String value){
        LinearLayout tile=Ui.column(this);Ui.pad(tile,this,12);tile.setBackground(Ui.surface(this,card(),14,line()));
        LinearLayout.LayoutParams params=new LinearLayout.LayoutParams(0,-2,1);params.setMargins(0,Ui.dp(this,4),Ui.dp(this,7),Ui.dp(this,4));host.addView(tile,params);
        tile.addView(Ui.text(this,label,10,muted(),true));tile.addView(Ui.text(this,value,20,accent(),true));
    }
'''
source = source.replace(anchor, methods, 1)
menu_anchor = '        section(body,"ACTIVE MODES");toggleRow(body,d,settingsOnly,"⚡","Turbo Boost"'
if source.count(menu_anchor) != 1:
    raise SystemExit("Control-center menu anchor mismatch; no Java changes applied.")
source = source.replace(menu_anchor, '        section(body,"ACTIVE MODES");actionRow(body,d,"✦","SR Turbo Pro dashboard","Live overview of tabs, downloads, protection and appearance","OPEN",true,this::proDashboard);toggleRow(body,d,settingsOnly,"⚡","Turbo Boost"', 1)
activity.write_text(source, encoding="utf-8")

build = gradle.read_text(encoding="utf-8")
if "versionCode 32" not in build or "versionName '3.6'" not in build:
    raise SystemExit("Unexpected app version; refusing to overwrite version metadata.")
build = build.replace("versionCode 32", "versionCode 33", 1).replace("versionName '3.6'", "versionName '3.7'", 1)
gradle.write_text(build, encoding="utf-8")
print("Applied SR Turbo Pro dashboard and version 3.7 (versionCode 33).")
