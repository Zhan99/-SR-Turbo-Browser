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
build = build.replace("versionCode 32", "versionCode 35", 1).replace("versionName '3.6'", "versionName '3.9'", 1)
gradle.write_text(build, encoding="utf-8")

# Pro 3.8 visual refresh: home screen, Control Center and Downloads Center.
downloads = root / "app/src/main/java/com/srcreation/browser/DownloadsActivity.java"
if not downloads.is_file():
    raise SystemExit("DownloadsActivity.java not found.")
source = activity.read_text(encoding="utf-8")
home_anchor = '        }else renderQuickAccess(panel);\n'
if source.count(home_anchor) != 1:
    raise SystemExit("Home screen insertion point mismatch.")
source = source.replace(home_anchor, '        }else renderQuickAccess(panel);\n', 1)
home_method_anchor = '    void defaultQuickLinks(){'
if source.count(home_method_anchor) != 1:
    raise SystemExit("Quick-access method insertion point mismatch.")
home_method = r'''    void renderProHome(LinearLayout panel){
        LinearLayout hero=Ui.column(this);Ui.pad(hero,this,17);
        hero.setBackground(Ui.gradient(this,palette().toolbar,palette().nav,22));
        LinearLayout brand=Ui.row(this);
        TextView brandName=Ui.text(this,"⚡  SR TURBO",12,palette().highlight,true);
        brandName.setLetterSpacing(0.12f);brand.addView(brandName,new LinearLayout.LayoutParams(0,-2,1));
        TextView edition=Ui.text(this,"PRO  •  3.8",10,Color.WHITE,true);
        edition.setBackground(Ui.bg(0x3346d4c2,10,this));Ui.pad(edition,this,7);brand.addView(edition);hero.addView(brand);
        TextView headline=Ui.text(this,"Browse beyond limits.",25,Color.WHITE,true);
        headline.setPadding(0,Ui.dp(this,14),0,Ui.dp(this,3));hero.addView(headline);
        hero.addView(Ui.text(this,"Fast browsing. Smarter downloads. Your controls, all in one place.",12,0xffd4e2ee,false));
        LinearLayout searchRow=Ui.row(this);searchRow.setGravity(Gravity.CENTER_VERTICAL);
        EditText query=new EditText(this);query.setSingleLine(true);query.setTextSize(14);query.setTextColor(Color.WHITE);query.setHintTextColor(0xffb9c9d8);
        query.setHint("Search the web or enter a website");query.setSelectAllOnFocus(true);
        query.setInputType(android.text.InputType.TYPE_CLASS_TEXT|android.text.InputType.TYPE_TEXT_VARIATION_URI);
        query.setImeOptions(EditorInfo.IME_ACTION_GO);query.setPadding(Ui.dp(this,12),0,Ui.dp(this,8),0);
        query.setBackground(Ui.bg(0x33202f43,14,this));
        query.setOnEditorActionListener((v,a,e)->{if(a==EditorInfo.IME_ACTION_GO||(e!=null&&e.getKeyCode()==KeyEvent.KEYCODE_ENTER&&e.getAction()==KeyEvent.ACTION_DOWN)){navigate(query.getText().toString());return true;}return false;});
        searchRow.addView(query,new LinearLayout.LayoutParams(0,Ui.dp(this,48),1));
        TextView go=Ui.button(this,"GO",Color.WHITE,palette().highlight,()->navigate(query.getText().toString()));
        go.setMinWidth(Ui.dp(this,54));LinearLayout.LayoutParams goLp=new LinearLayout.LayoutParams(-2,Ui.dp(this,46));goLp.leftMargin=Ui.dp(this,7);searchRow.addView(go,goLp);
        LinearLayout.LayoutParams searchLp=new LinearLayout.LayoutParams(-1,-2);searchLp.topMargin=Ui.dp(this,15);hero.addView(searchRow,searchLp);
        LinearLayout stats=Ui.row(this);stats.setPadding(0,Ui.dp(this,14),0,0);
        String[] labels={"TABS  "+tabs.size()+"/20","THEME  "+theme.title,"TURBO  "+(turbo()?"ON":"OFF")};
        for(int i=0;i<labels.length;i++){TextView chip=Ui.text(this,labels[i],10,Color.WHITE,true);chip.setGravity(Gravity.CENTER);chip.setBackground(Ui.bg(0x33485c72,10,this));Ui.pad(chip,this,7);LinearLayout.LayoutParams cp=new LinearLayout.LayoutParams(0,-2,1);cp.setMargins(0,0,Ui.dp(this,5),0);stats.addView(chip,cp);}
        hero.addView(stats);
        LinearLayout.LayoutParams hp=new LinearLayout.LayoutParams(-1,-2);hp.bottomMargin=Ui.dp(this,10);panel.addView(hero,hp);
        LinearLayout quick=Ui.row(this);quick.setGravity(Gravity.CENTER_VERTICAL);
        TextView downloads=Ui.button(this,"↓  Downloads",fg(),card(),this::downloads);
        TextView video=Ui.button(this,"▶  Video",fg(),card(),this::videoPicker);
        TextView menu=Ui.button(this,"☷  Control center",fg(),card(),()->showControlCenter(false));
        for(TextView b:new TextView[]{downloads,video,menu}){LinearLayout.LayoutParams bp=new LinearLayout.LayoutParams(0,-2,1);bp.setMargins(0,0,Ui.dp(this,5),0);quick.addView(b,bp);}
        LinearLayout.LayoutParams qp=new LinearLayout.LayoutParams(-1,-2);qp.bottomMargin=Ui.dp(this,6);panel.addView(quick,qp);
    }
'''
# Hero card intentionally omitted; keep compact Quick Access home.
cc_anchor = '        section(body,"ACTIVE MODES");actionRow(body,d,"✦","SR Turbo Pro dashboard"'
if source.count(cc_anchor) != 1:
    raise SystemExit("Control-center insertion point mismatch.")
banner = r'''        LinearLayout workspace=Ui.column(this);Ui.pad(workspace,this,13);
        workspace.setBackground(Ui.gradient(this,palette().toolbar,palette().nav,17));
        workspace.addView(Ui.text(this,"PRO WORKSPACE",10,palette().highlight,true));
        workspace.addView(Ui.text(this,"Everything in one place",18,Color.WHITE,true));
        workspace.addView(Ui.text(this,tabs.size()+" tabs  •  "+connections+" connections  •  "+theme.title,11,0xffd4e2ee,false));
        LinearLayout.LayoutParams workspaceLp=new LinearLayout.LayoutParams(-1,-2);workspaceLp.bottomMargin=Ui.dp(this,5);body.addView(workspace,workspaceLp);
'''
source = source.replace(cc_anchor, banner+cc_anchor, 1)
activity.write_text(source, encoding="utf-8")

ds = downloads.read_text(encoding="utf-8")
field_anchor = 'LinearLayout list;TextView summary,speedLabel,transferLabel;boolean dark;'
if ds.count(field_anchor) != 1:
    raise SystemExit("Downloads fields anchor mismatch.")
ds = ds.replace(field_anchor, 'LinearLayout list,filterBar;TextView summary,speedLabel,transferLabel;String filter="ALL";boolean dark;', 1)
ui_anchor = 'root.addView(summary);root.addView(Ui.button(this,"▶  Video downloads"'
if ds.count(ui_anchor) != 1:
    raise SystemExit("Downloads UI anchor mismatch.")
ds = ds.replace(ui_anchor, 'root.addView(summary);filterBar=Ui.row(this);filterBar.setPadding(Ui.dp(this,12),Ui.dp(this,5),Ui.dp(this,12),Ui.dp(this,8));root.addView(filterBar);renderFilters();root.addView(Ui.button(this,"▶  Video downloads"', 1)
refresh_anchor = 'void refresh(){List<JSONObject> items=DownloadService.snapshot(this);long aggregate=0;int running=0,queued=0;'
if ds.count(refresh_anchor) != 1:
    raise SystemExit("Downloads refresh anchor mismatch.")
ds = ds.replace(refresh_anchor, 'void refresh(){List<JSONObject> all=DownloadService.snapshot(this);long aggregate=0;int running=0,queued=0;', 1)
summary_anchor = 'speedLabel.setText(size(aggregate)+"/s");transferLabel.setText(running+" active  ·  "+queued+" queued");summary.setText(items.size()+" transfers  •  Download/SR Turbo");StringBuilder order=new StringBuilder();for(JSONObject j:items)'
if ds.count(summary_anchor) != 1:
    raise SystemExit("Downloads summary anchor mismatch.")
ds = ds.replace(summary_anchor, 'speedLabel.setText(size(aggregate)+"/s");transferLabel.setText(running+" active  ·  "+queued+" queued");summary.setText(all.size()+" transfers  •  Download/SR Turbo");List<JSONObject> items=new ArrayList<>();for(JSONObject item:all){String state=item.optString("state");if(filter.equals("ALL")||(filter.equals("ACTIVE")&&(state.equals("Running")||state.equals("Queued")||state.equals("Saving")||state.equals("Paused")))||(filter.equals("COMPLETED")&&state.equals("Completed"))||(filter.equals("FAILED")&&(state.equals("Failed")||state.equals("Cancelled"))))items.add(item);}StringBuilder order=new StringBuilder();for(JSONObject j:items)', 1)
empty_anchor = 'if(items.isEmpty()){TextView empty=Ui.text(this,"No downloads yet.\\nOpen a website or paste a direct download link.",16,muted(),false);'
if ds.count(empty_anchor) != 1:
    raise SystemExit("Downloads empty-state anchor mismatch.")
ds = ds.replace(empty_anchor, 'if(items.isEmpty()){String emptyText=filter.equals("ALL")?"No downloads yet.\\nOpen a website or paste a direct download link.":"No "+filter.toLowerCase(Locale.ROOT)+" transfers.";TextView empty=Ui.text(this,emptyText,16,muted(),false);', 1)
filter_anchor = '    final Runnable update=new Runnable(){'
if ds.count(filter_anchor) != 1:
    raise SystemExit("Downloads filter method anchor mismatch.")
filters = r'''    void renderFilters(){
        filterBar.removeAllViews();
        String[] labels={"ALL","ACTIVE","COMPLETED","FAILED"};
        for(String value:labels){
            boolean selected=filter.equals(value);
            TextView chip=Ui.button(this,value,selected?Color.WHITE:fg(),selected?theme.nav:card(),()->{filter=value;last="";renderFilters();refresh();});
            chip.setTextSize(10);chip.setPadding(Ui.dp(this,10),Ui.dp(this,9),Ui.dp(this,10),Ui.dp(this,9));
            LinearLayout.LayoutParams lp=new LinearLayout.LayoutParams(0,-2,1);lp.setMargins(0,0,Ui.dp(this,5),0);filterBar.addView(chip,lp);
        }
    }
'''
ds = ds.replace(filter_anchor, filters+filter_anchor, 1)
ds = ds.replace('selected?Color.WHITE:fg()', 'selected?android.graphics.Color.WHITE:fg()')
ds = ds.replace('queued=0;for(JSONObject j:items){', 'queued=0;for(JSONObject j:all){')
downloads.write_text(ds, encoding="utf-8")

build = gradle.read_text(encoding="utf-8")
if "versionCode 33" not in build or "versionName '3.7'" not in build:
    raise SystemExit("Unexpected patched app version.")
gradle.write_text(build.replace("versionCode 33","versionCode 34",1).replace("versionName '3.7'","versionName '3.8'",1),encoding="utf-8")
# Expand the offline theme gallery from 18 to 30 color palettes.
theme_file = root / "app/src/main/java/com/srcreation/browser/BrowserTheme.java"
theme_source = theme_file.read_text(encoding="utf-8")
theme_anchor = '    MOONLAKE("Moonlit Lake", "Moonlight · quiet woodland", "moonlake", true, 0xff171e3c,0xff293552,0xff1e2945,0xff2c3b58,0xffeef3ff,0xffc0cde9,0xffbcd9ff,0xffbcd9ff,0xff4d6080,0xff3d5478);'
if theme_source.count(theme_anchor) != 1:
    raise SystemExit("BrowserTheme enum anchor mismatch; refusing to change theme list.")
extra_themes = """    MOONLAKE("Moonlit Lake", "Moonlight · quiet woodland", "moonlake", true, 0xff171e3c,0xff293552,0xff1e2945,0xff2c3b58,0xffeef3ff,0xffc0cde9,0xffbcd9ff,0xffbcd9ff,0xff4d6080,0xff3d5478),
    GRAPHITE("Graphite Pro", "Charcoal · electric silver", null, true, 0xff171b22,0xff292f39,0xff202630,0xff2c333e,0xfff2f5fa,0xffb6c0ce,0xff8ba7c7,0xffc6dcf5,0xff414c5c,0xff35485f),
    COBALT("Cobalt Blue", "Deep blue · vivid cyan", null, true, 0xff102a50,0xff1a3d6b,0xff17365d,0xff204574,0xfff1f7ff,0xffbfd4f2,0xff4fa9ff,0xff8bd4ff,0xff3a5c86,0xff234d78),
    CRIMSON("Crimson Night", "Dark cherry · ruby glow", null, true, 0xff351b2b,0xff51283b,0xff422236,0xff583047,0xfffff2f6,0xffe0b9c8,0xffff6b91,0xffffa5bc,0xff75475c,0xff68374f),
    COPPER("Copper Luxe", "Warm bronze · premium dark", null, true, 0xff38291f,0xff59402e,0xff483528,0xff5b4434,0xfffff6ed,0xffdfc7b2,0xffd58b55,0xffffc18d,0xff795c49,0xff6b4a35),
    MIDNIGHT("Midnight Violet", "Deep indigo · violet light", null, true, 0xff211d43,0xff332d5e,0xff29254f,0xff393365,0xfff5f1ff,0xffc9c2eb,0xffa48bff,0xffc7b8ff,0xff5a5485,0xff494174),
    ORCHID("Orchid Bloom", "Soft lilac · plum accents", null, false, 0xff50365e,0xff684878,0xfffaf5ff,0xffffffff,0xff352443,0xff6d5a7d,0xff8653a8,0xffe6c5ff,0xffe3d4ed,0xfff0e3f8),
    GLACIER("Glacier Ice", "Frost white · arctic blue", null, false, 0xff24516c,0xff326b88,0xfff1faff,0xffffffff,0xff17394c,0xff4d7184,0xff187a9e,0xffb9edff,0xffd2e7ef,0xffdff4fb),
    SANDSTONE("Sandstone", "Natural beige · earthy olive", null, false, 0xff5b4934,0xff786144,0xfffff8ec,0xfffffdf6,0xff3f3426,0xff75664f,0xff8b6b37,0xffffdf9c,0xffe8dcc5,0xfff5ead2),
    CYBERPUNK("Cyber Pulse", "Neon teal · futuristic dark", null, true, 0xff101f2b,0xff183342,0xff152b38,0xff1d3948,0xffedffff,0xffafd2d9,0xff00d6c9,0xff7dfff2,0xff3c6670,0xff245b5a),
    SLATE("Slate Minimal", "Cool grey · restrained blue", null, false, 0xff344253,0xff48596d,0xfff2f5f8,0xffffffff,0xff253343,0xff586879,0xff3d668f,0xffc4dcf5,0xffd7e0e8,0xffe5edf4),
    CORAL("Coral Breeze", "Warm white · tropical coral", null, false, 0xff713d3b,0xff92504a,0xfffff6f1,0xffffffff,0xff4c302d,0xff80635e,0xffc65e50,0xffffc2ae,0xffeedbd4,0xfff8e6df),
    OLIVE("Olive Grove", "Soft cream · botanical olive", null, false, 0xff465035,0xff5d6b43,0xfff7f8ed,0xffffffff,0xff333c25,0xff657052,0xff657d32,0xffd9e8a8,0xffe0e5d0,0xffedf1d9);"""
theme_source = theme_source.replace(theme_anchor, extra_themes, 1)
theme_file.write_text(theme_source, encoding="utf-8")

print("Applied SR Turbo Browser Pro 3.9 home and theme update.")

