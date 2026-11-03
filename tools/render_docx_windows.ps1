param([Parameter(Mandatory=$true)][string]$InputFile,[Parameter(Mandatory=$true)][string]$OutputFile)
$ErrorActionPreference='Stop'
$taskInput=[IO.Path]::GetFullPath($InputFile)
$taskOutput=[IO.Path]::GetFullPath($OutputFile)
New-Item -ItemType Directory -Force -Path ([IO.Path]::GetDirectoryName($taskOutput)) | Out-Null
$word=New-Object -ComObject Word.Application
$word.Visible=$false
$word.DisplayAlerts=0
$document=$null
try {
  $document=$word.Documents.Open($taskInput,$false,$true,$false)
  $document.Repaginate()
  $document.ExportAsFixedFormat($taskOutput,17)
  Write-Output ($document.ComputeStatistics(2).ToString()+' pages: '+$taskOutput)
} finally {
  if($null -ne $document){$document.Close(0);[Runtime.InteropServices.Marshal]::FinalReleaseComObject($document)|Out-Null}
  $word.Quit()
  [Runtime.InteropServices.Marshal]::FinalReleaseComObject($word)|Out-Null
}
