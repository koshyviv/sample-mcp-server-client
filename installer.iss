[Setup]
AppName=MCP Client X
AppVersion=1.0.0
AppPublisher=MCP Client X Team
AppPublisherURL=https://github.com/your-repo/mcp-client-x
AppSupportURL=https://github.com/your-repo/mcp-client-x/issues
AppUpdatesURL=https://github.com/your-repo/mcp-client-x/releases
DefaultDirName={autopf}\MCP Client X
DefaultGroupName=MCP Client X
AllowNoIcons=yes
LicenseFile=LICENSE.txt
OutputDir=dist_installer
OutputBaseFilename=MCP_Client_X_Setup
SetupIconFile=icon.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1; Check: not IsAdminInstallMode

[Files]
Source: "dist\MCP_Client_X.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "requirements.txt"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\MCP Client X"; Filename: "{app}\MCP_Client_X.exe"
Name: "{group}\{cm:UninstallProgram,MCP Client X}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\MCP Client X"; Filename: "{app}\MCP_Client_X.exe"; Tasks: desktopicon
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\MCP Client X"; Filename: "{app}\MCP_Client_X.exe"; Tasks: quicklaunchicon

[Run]
Filename: "{app}\MCP_Client_X.exe"; Description: "{cm:LaunchProgram,MCP Client X}"; Flags: nowait postinstall skipifsilent

[Code]
procedure InitializeWizard;
begin
  WizardForm.LicenseAcceptedRadio.Checked := True;
end; 