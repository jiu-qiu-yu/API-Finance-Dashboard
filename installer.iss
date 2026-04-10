; Inno Setup Script for API Finance Dashboard
; Build command: iscc installer.iss
;
; Installer wizard flow:
;   1. Welcome page (with sidebar logo)
;   2. License agreement (MIT)
;   3. Select installation directory
;   4. Select Start Menu folder
;   5. Additional tasks (desktop icon)
;   6. Ready to install summary
;   7. Installing... (progress bar)
;   8. Finish page (launch option)

#define MyAppName "API Finance Dashboard"
#define MyAppChineseName "API站长财务看板"
#define MyAppExeName "api-finance-dashboard.exe"
#define MyAppPublisher "API Chancellor"
#define MyAppURL "https://github.com/jiu-qiu-yu/API_Chancellor"

; Version is injected by build script, default to 0.1.0
#ifndef MyAppVersion
  #define MyAppVersion "0.1.0"
#endif

[Setup]
AppId={{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}/issues
AppContact={#MyAppURL}/issues

; Installation directory (user can change this in the wizard)
DefaultDirName={autopf}\{#MyAppName}
; Allow user to change directory
DisableDirPage=no
; Start Menu group (user can change this in the wizard)
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=no
; Allow the user to disable Start Menu group creation
AllowNoIcons=yes

; License agreement page
LicenseFile=LICENSE

; Output
OutputDir=dist
OutputBaseFilename=API-Finance-Dashboard-Setup-{#MyAppVersion}

; Icons and branding
SetupIconFile=logo\logo.ico
UninstallDisplayIcon={app}\{#MyAppExeName}
UninstallDisplayName={#MyAppName}

; Wizard images (sidebar 164x314, small 55x55)
WizardImageFile=installer_assets\wizard_image.bmp
WizardSmallImageFile=installer_assets\wizard_small_image.bmp
WizardStyle=modern

; Compression
Compression=lzma2/ultra64
SolidCompression=yes

; Privileges: per-user install by default, can elevate to admin
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog

; Version info embedded in installer .exe properties
VersionInfoVersion={#MyAppVersion}
VersionInfoCompany={#MyAppPublisher}
VersionInfoDescription={#MyAppChineseName} - 安装程序
VersionInfoProductName={#MyAppName}
VersionInfoProductVersion={#MyAppVersion}

; Minimum Windows version
MinVersion=10.0

[Languages]
Name: "chinesesimplified"; MessagesFile: "installer_assets\ChineseSimplified.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"

[Files]
Source: "dist\api-finance-dashboard\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
; Start Menu shortcuts
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Comment: "{#MyAppChineseName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
; Desktop shortcut (optional, user chooses in wizard)
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon; Comment: "{#MyAppChineseName}"

[Run]
; "Launch application" checkbox on finish page
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; Clean up runtime cache, but preserve user data (~/.api-finance-dashboard/)
Type: filesandordirs; Name: "{app}\__pycache__"

[Messages]
; Custom welcome message
WelcomeLabel2=This will install [name/ver] on your computer.%n%nAPI站长自动化财务看板 - 自动采集多个API平台的余额与消费数据，实时计算利润。%n%nIt is recommended that you close all other applications before continuing.
