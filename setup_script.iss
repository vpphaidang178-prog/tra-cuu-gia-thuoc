[Setup]
AppName=Tra Cuu Gia Thuoc
AppVersion=2.0.0
DefaultDirName={autopf}\Tra Cuu Gia Thuoc
DefaultGroupName=Tra Cuu Gia Thuoc
OutputDir=.
OutputBaseFilename=setup_tracuugiathuoc
Compression=lzma
SolidCompression=yes
ArchitecturesInstallIn64BitMode=x64

[Files]
Source: "dist\Tra Cuu Gia Thuoc\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\Tra Cuu Gia Thuoc"; Filename: "{app}\Tra Cuu Gia Thuoc.exe"
Name: "{commondesktop}\Tra Cuu Gia Thuoc"; Filename: "{app}\Tra Cuu Gia Thuoc.exe"

[Run]
Filename: "{app}\Tra Cuu Gia Thuoc.exe"; Description: "Launch application"; Flags: nowait postinstall skipifsilent
