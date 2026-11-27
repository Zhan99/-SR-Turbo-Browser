#!/usr/bin/env bash
set -euo pipefail
ROOT="${1:?Android project root required}"
python3 - "$ROOT" <<'PY'
from pathlib import Path
import sys
root=Path(sys.argv[1])
def edit(rel, pairs):
    p=root/rel
    s=p.read_text(encoding="utf-8")
    for old,new in pairs:
        if old not in s:
            raise SystemExit(f"Patch anchor not found in {rel}: {old[:100]!r}")
        s=s.replace(old,new,1)
    p.write_text(s,encoding="utf-8")
edit("app/src/main/java/com/srcreation/browser/YouTubeDownloadService.java",[
('static volatile boolean compatibilityMode=false;','static volatile boolean compatibilityMode=false, audioOnly=false;'),
('static volatile String state="Ready", detail="", resultUri="", resultName="", jobId="", engineVersion="";','static volatile String state="Ready", detail="", resultUri="", resultName="", resultMime="video/mp4", jobId="", engineVersion="";'),
('resultName=p.getString("name","");','resultName=p.getString("name","");resultMime=p.getString("mime","video/mp4");'),
('.putString("name",resultName).putString("engine_version",engineVersion)','.putString("name",resultName).putString("mime",resultMime).putString("engine_version",engineVersion)'),
('final int quality=update?720:YouTubeLinks.quality(i.getIntExtra("quality",720));','final int quality=update?720:YouTubeLinks.quality(i.getIntExtra("quality",720));\n        audioOnly=!update&&!batch&&i.getBooleanExtra("audio_only",false);'),
('if(!update){resultUri="";resultName="";}persist();','if(!update){resultUri="";resultName="";resultMime=audioOnly?"audio/mpeg":"video/mp4";}persist();'),
('.addOption("--retry-sleep","fragment:exp=2:30").addOption("--format",SiteVideoLinks.format(url,quality)).addOption("--merge-output-format","mp4").addOption("--progress")',
'.addOption("--retry-sleep","fragment:exp=2:30");\n        if(audioOnly){request.addOption("--format","bestaudio/best").addOption("-x").addOption("--audio-format","mp3").addOption("--audio-quality","0");}\n        else{request.addOption("--format",SiteVideoLinks.format(url,quality)).addOption("--merge-output-format","mp4");}\n        request.addOption("--progress")'),
('File[] files=dir.listFiles(f->f.isFile()&&f.getName().endsWith(".mp4")&&f.length()>0);\n                if(files==null||files.length!=1)throw new IOException("Expected one complete MP4; no file was published.");\n                File file=files[0];state="Saving";detail=prefix+"Saving MP4 to Downloads…";rate=eta=-1;persist();\n                ContentValues v=new ContentValues();v.put(MediaStore.Downloads.DISPLAY_NAME,DownloadService.safeName(file.getName()));v.put(MediaStore.Downloads.MIME_TYPE,"video/mp4");',
'String extension=audioOnly?".mp3":".mp4";\n                File[] files=dir.listFiles(f->f.isFile()&&f.getName().toLowerCase(Locale.ROOT).endsWith(extension)&&f.length()>0);\n                if(files==null||files.length!=1)throw new IOException("Expected one complete "+(audioOnly?"MP3 audio":"MP4 video")+" file; no file was published.");\n                File file=files[0];String outputMime=audioOnly?"audio/mpeg":"video/mp4";state="Saving";detail=prefix+(audioOnly?"Saving MP3 audio":"Saving MP4 video")+" to Downloads…";rate=eta=-1;persist();\n                ContentValues v=new ContentValues();v.put(MediaStore.Downloads.DISPLAY_NAME,DownloadService.safeName(file.getName()));v.put(MediaStore.Downloads.MIME_TYPE,outputMime);'),
('resultUri=pending.toString();resultName=file.getName();pending=null;','resultUri=pending.toString();resultName=file.getName();resultMime=outputMime;pending=null;'),
('message="Saved to "+folder;','message="Saved "+(audioOnly?"MP3 audio":"MP4 video")+" to "+folder;')
])
edit("app/src/main/java/com/srcreation/browser/YouTubeDownloadsActivity.java",[
('EditText url;Spinner quality;CheckBox permission;','EditText url;Spinner quality;CheckBox permission,audioOnly;'),
('permission=new CheckBox(this);permission.setText(batch?"I have permission to download every selected video.":"I have permission to download this video.");permission.setTextColor(fg());panel.addView(permission);',
'audioOnly=new CheckBox(this);audioOnly.setText("Download audio only (MP3)");audioOnly.setTextColor(fg());audioOnly.setChecked(false);audioOnly.setVisibility(batch?View.GONE:View.VISIBLE);panel.addView(audioOnly);\n        permission=new CheckBox(this);permission.setText(batch?"I have permission to download every selected video.":"I have permission to download this video/audio.");permission.setTextColor(fg());panel.addView(permission);'),
('setAction(YouTubeDownloadService.START).putExtra("url",link).putExtra("quality",heights[quality.getSelectedItemPosition()])','setAction(YouTubeDownloadService.START).putExtra("url",link).putExtra("quality",heights[quality.getSelectedItemPosition()]).putExtra("audio_only",audioOnly.isChecked())'),
('setDataAndType(u,"video/mp4")','setDataAndType(u,YouTubeDownloadService.resultMime)'),
('Open last saved video','Open last saved media'),
('permission.setEnabled(!busy);for(CheckBox c:choices)','permission.setEnabled(!busy);audioOnly.setEnabled(!busy);for(CheckBox c:choices)')
])
edit("app/src/main/java/com/srcreation/browser/BrowserActivity.java",[
('if(!http(url)){toast("Only HTTP/HTTPS file downloads are supported");return;}\n         String guess=URLUtil.guessFileName(url,disposition,mime);',
'url=url==null?"":url.trim();\n         if(!http(url)){toast("This link is not a direct HTTP/HTTPS file URL. Open the file page and use its Download link, or copy the direct file address.");return;}\n         // GitHub /blob/ pages return HTML; switch to the raw file endpoint before downloading.\n         try{android.net.Uri parsed=android.net.Uri.parse(url);if("github.com".equalsIgnoreCase(parsed.getHost())&&parsed.getPath()!=null&&parsed.getPath().contains("/blob/"))url=parsed.buildUpon().encodedPath(parsed.getPath().replaceFirst("/blob/","/raw/")).build().toString();}catch(Exception ignored){}\n         String guess=URLUtil.guessFileName(url,disposition,mime);'),
('String type=mime==null?(inferred==null?"application/octet-stream":inferred):mime.split(";",2)[0];',
'String supplied=mime==null?"":mime.split(";",2)[0].trim();\n         String type=(supplied.isEmpty()||supplied.equalsIgnoreCase("text/html")||supplied.equalsIgnoreCase("application/octet-stream"))?(inferred==null?"application/octet-stream":inferred):supplied;'),
('static boolean http(String s){return s!=null&&(s.startsWith("https://")||s.startsWith("http://"));}',
'static boolean http(String s){if(s==null)return false;String v=s.trim().toLowerCase(Locale.ROOT);return v.startsWith("https://")||v.startsWith("http://");}'),
('    void quickVideoDownload(String link){\n        if(link==null){startActivity(new Intent(this,YouTubeDownloadsActivity.class));return;}\n        if(YouTubeDownloadService.busy){toast("A video download is already running");return;}',
'    void quickVideoDownload(String link){\n        if(link==null){startActivity(new Intent(this,YouTubeDownloadsActivity.class));return;}\n        if(YouTubeDownloadService.busy){toast("A video/audio download is already running");return;}'),
('startActivity(new Intent(this,YouTubeDownloadsActivity.class));\n    }\n    void backgroundDownloadSettings()',
'startActivity(new Intent(this,YouTubeDownloadsActivity.class).putExtra("url",link));\n    }\n    void backgroundDownloadSettings()')
])
print("Applied audio-only MP3 mode, result MIME handling, GitHub raw-file routing, and generic MIME inference.")
PY
