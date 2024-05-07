# No multiline strings have been used to improve code readability

$ErrorActionPreference = "Stop"

# Make sure we are running the script correctly (using the .bat file)


function Get-IniContent($FilePath) { # Source: https://devblogs.microsoft.com/scripting/use-powershell-to-work-with-any-ini-file/
    $ini = @{}
    switch -regex -file $FilePath
    {
        "^\[(.+)\]" # Section
        {
            $section = $matches[1]
            $ini[$section] = @{}
            $CommentCount = 0
        }
        "^(;.*)$" # Comment
        {
            $value = $matches[1]
            $CommentCount = $CommentCount + 1
            $name = "Comment" + $CommentCount
            $ini[$section][$name] = $value
        }
        "(.+?)\s* ?= ?(.*)" # Key
        {
            $name,$value = $matches[1..2]
            $ini[$section][$name] = $value
        }
    }
    return $ini
}


function Out-IniFile($InputObject, $FilePath) { # Source https://devblogs.microsoft.com/scripting/use-powershell-to-work-with-any-ini-file/
    $outFile = New-Item -ItemType file -Path $Filepath
    foreach ($i in $InputObject.keys)
    {
        if (!($($InputObject[$i].GetType().Name) -eq "Hashtable"))
        {
            # No Sections
            Add-Content -Path $outFile -Value "$i=$($InputObject[$i])"
        } else {
            # Sections
            Add-Content -Path $outFile -Value "[$i]"
            foreach ($j in ($InputObject[$i].keys | Sort-Object))
            {
                if ($j -match "^Comment[\d]+") {
                    Add-Content -Path $outFile -Value "$($InputObject[$i][$j])"
                } else {
                    Add-Content -Path $outFile -Value "$j=$($InputObject[$i][$j])"
                }

            }
            Add-Content -Path $outFile -Value ""
        }
    }
}


if (Test-Path ".\main") {
    Set-Location ".\main"
} else {
    Write-Host ""
    Write-Host "================================================================>"
    Write-Host "It appears your installation is corrupted."
    Write-Host "This script should've been launched with the Current Working Directory set as the root repository folder"
    Write-Host "The root repository folder is named 'Self-HostedSimpleDiscordBot' by default renaming is supported"
    Write-Host "Unfortunately the Current Working Directory is $(Get-Location)"
    Write-Host ""
    Write-Host "The script will stop because continuing is be dangerous and may irreversibly modify files outside the folder."
    Write-Host "Please try re-downloading or verifying if all the files are placed in the correct locations"
    Write-Host ""
    Write-Host "This script will exit now..."
    Write-Host "<================================================================"
    Write-Host ""
    exit
}


# Variables

$ConfigPath = ".\config.ini"
$ConfigData = Get-IniContent -FilePath $ConfigPath
$ConfigMain = $ConfigData["MAIN"]

$MinimumPythonVersionContent = $ConfigMain["MinimumPythonVersion"]
$MinimumPythonVersionIsSupportedFormat = $MinimumPythonVersionContent -match '^(\d+)\.(\d+)\.(\d+)'
if (-not $MinimumPythonVersionIsSupportedFormat) {
    Write-Host ""
    Write-Host "==============================================>"
    Write-Host "Python version defined at '$($ConfigPath)' is of unsupported format"
    Write-Host "Please verify the file's content and use the format major.minor.patch"
    Write-Host ""
    Write-Host "This script will exit now..."
    Write-Host "<============================================="
    Write-Host ""
    exit
}
$MinimumPythonVersionMajor = $Matches[1]
$MinimumPythonVersionMinor = $Matches[2]
$MinimumPythonVersionPatch = $Matches[3]

$UserPythonVersion = ( python --version )
$null = $UserPythonVersion -match "^(Python )(\d+)\.(\d+)\.(\d+)"
$UserPythonVersionMajor = $Matches[2]
$UserPythonVersionMinor = $Matches[3]
$UserPythonVersionPatch = $Matches[4]

# We ignore the patch because of how Semantic Versioning (SemVer) works
$UsingCorrectPythonVersion = ( ( $UserPythonVersionMajor -ge $MinimumPythonVersionMajor ) -and ( $UserPythonVersionMinor -ge $MinimumPythonVersionMinor ) )

if ( -not $usingCorrectPythonVersion ) {
    Write-Host ""
    Write-Host "================================================>"
    Write-Host "Sadly your Python is not supported..."
    Write-Host "Current Python Version $UserPythonVersionMajor.$UserPythonVersionMinor.$UserPythonVersionPatch"
    Write-Host "Minimum Python Version: $MinimumPythonVersionMajor.$MinimumPythonVersionMinor.0"
    Write-Host ""
    Write-Host "The script will exit now..."
    Write-Host "<================================================"
    Write-Host ""
    exit
}


$RequirementsFilePath = $ConfigMain["PathRequirements"]
$Requirements_Content = ( Get-Content -Path $RequirementsFilePath )

# Python file exit codes:
$OverrideRetryExitCode = 1001

$PythonVersionComment_Correct_Above =  "      \/--------------------------------\/"
$PythonVersionComment_Correct =           "   *** C O R R E C T  V E R S I O N ! ! ! ***"
$PythonVersionComment_Correct_Below = "      /\--------------------------------/\"

$VenvError_FirstTimeWrongAnswer = $true

$RestartBotIfStops = $false
$RestartBotIfStops_Answer_FirstTimeWrongAnswer = $true
$ResetDiscordBotToken_FirstTimeWrongAnswer = $true
$RestartBotIfStops_Answer = $false
$BotRetryDoBreak = $false

$PathMainScript = $ConfigMain["PathMainScript"]
$PathResetToken = $ConfigMain["PathResetToken"]

$FirstBadAnswerSleepSeconds = $ConfigMain["FirstBadAnswerSleepSeconds"]

$BotCurrentRetriesCount = 0
$BotMaxRetriesCount = 3600
$BotRetrySleepSeconds = 10

$VenvName = "venv"
$VenvPath = "./$($VenvName)"

if (-not (Test-Path $VenvPath)) {
    Write-Host ""
    Write-Host "----------------------------------->"
    Write-Host "Creating a New Virtual Environment!"
    Write-Host "<-----------------------------------"
    Write-Host ""

    try {
        python -m venv venv
    } catch {
        Write-Host ""
        Write-Host "=========================================================>"
        Write-Host "Something went wrong!"
        Write-Host "While Creating a New Virtual Environment at $($VenvPath)!"
        Write-Host ""
        Write-Host "    Error Message:"
        Write-Host "*   $($_)"
        Write-Host ""
        Write-Host "The script will exit now!"
        Write-Host "<========================================================="
        Write-Host ""

        exit
    }
}

Write-Host ""
Write-Host "----------------------------------------------->"
Write-Host "Attempting to activate the Virtual Environment!"
Write-Host "<-----------------------------------------------"
Write-Host ""

$PathVenvActivateScript = $ConfigMain["PathVenvActivateScript"]

try {
    . $PathVenvActivateScript
} catch {
    Write-Host ""
    Write-Host "======================================>"
    Write-Host "Failed to apply the Virtual Environment"
    Write-Host ""
    Write-Host "$($_.Exception.Message)"
    Write-Host ""
    Write-Host "The Script Will Attempt To Create A New Virtual Environment"
    Write-Host "<======================================"
    Write-Host ""

    try {
        python -m venv venv
    } catch {
        Write-Host ""
        Write-Host "======================================>"
        Write-Host "Failed to create the Virtual Environment"
        Write-Host ""
        Write-Host "$($_.Exception.Message)"
        Write-Host ""
        Write-Host "This script will now Exit"
        Write-Host "<======================================"
        Write-Host ""
        exit
    }

    Write-Host ""
    Write-Host "-------------------------------------------->"
    Write-Host "New Virtual Environment successfully created!"
    Write-Host "<--------------------------------------------"
    Write-Host ""
}


Write-Host ""
Write-Host "---------------------------------------------------->"
Write-Host "Making sure all the necessary modules are installed in the Virtual Environment."
Write-Host "<----------------------------------------------------"
Write-Host ""

pip install -r $RequirementsFilePath --disable-pip-version-check

$TokenEncrypted = $ConfigMain["token_ciphered_base64encoded_utf8"]

if ($TokenEncrypted.Length -ne 0) {

    while ($true) {

        Write-Host ""
        Write-Host "------------------------------------------------------------------------------->"
        Write-Host "QUESTION:"
        Write-Host "    You already passed a Discord Bot Token previously..."
        Write-Host "    Do You want to use the same Token? (Y/N)"
        $ResetDiscordBotToken_Answer = Read-Host

        $ResetDiscordBotToken_Answer_ToLower = $ResetDiscordBotToken_Answer.ToLower()

        if ($ResetDiscordBotToken_Answer_ToLower -eq "y") {

            Write-Host "Registered answer: Y. The previous Token will be used. Continuing the script..."
            Write-Host "<-------------------------------------------------------------------------------"
            break

        } elseif ($ResetDiscordBotToken_Answer_ToLower -eq "n") {

            python "$($PathResetToken)"

            Write-Host "Registered answer: N. The Token has been cleared..."
            Write-Host "You will be asked to input a new token Soon..."
            Write-Host "<-------------------------------------------------------------------------------"
            break

        } else {
            Write-Host ""
            Write-Host "-------------------------------------->"
            Write-Host "YOUR ANSWER:"
            Write-Host $ResetDiscordBotToken_Answer
            Write-Host "WASN'T " '"Y", NOR "N"'

            if ($ResetDiscordBotToken_FirstTimeWrongAnswer -eq $true) {

                $ResetDiscordBotToken_FirstTimeWrongAnswer = $false

                Write-Host "Repeating the question in 3 seconds..."
                Write-Host "<--------------------------------------"
                Start-Sleep -Seconds $FirstBadAnswerSleepSeconds

            } else {

                Write-Host "Repeating the question..."
                Write-Host "<--------------------------------------"

            }
        }

    }

}


while ($true) {
    Write-Host ""
    Write-Host "----------------------------------------------------------------------------------->"
    Write-Host "QUESTION:"
    Write-Host "    Do You want to automatically restart the bot in case it crashes or stops? (Y/N)"
    $RestartBotIfStops_Answer = Read-Host

    $RestartBotIfStops_Answer_ToLower = $RestartBotIfStops_Answer.ToLower()

    if ($RestartBotIfStops_Answer_ToLower -eq "y") {

        $RestartBotIfStops = $true
        Write-Host "Registered answer: Y. The bot WILL automatically restart."
        Write-Host "<-----------------------------------------------------------------------------------"
        break

    } elseif ($RestartBotIfStops_Answer_ToLower -eq "n") {

        $RestartBotIfStops = $false
        Write-Host "Registered answer: N. The bot WON'T automatically restart."
        Write-Host "<-----------------------------------------------------------------------------------"
        break

    } else {

        Write-Host ""
        Write-Host "-------------------------------------->"
        Write-Host "YOUR ANSWER:"
        Write-Host $RestartBotIfStops_Answer
        Write-Host "WASN'T " '"Y", NOR "N"'

        if (($RestartBotIfStops_Answer_FirstTimeWrongAnswer -eq $true) ) {

            $RestartBotIfStops_Answer_FirstTimeWrongAnswer = $false

            Write-Host "Repeating the question in 3 seconds..."
            Write-Host "<--------------------------------------"
            Start-Sleep -Seconds $FirstBadAnswerSleepSeconds

        } else {

            Write-Host "Repeating the question..."
            Write-Host "<--------------------------------------"

        }

    }

}


Write-Host ""
Write-Host "------------------------->"
Write-Host "Setup Finished!"
Write-Host "Starting the Discord bot!"
Write-Host "<-------------------------"
Write-Host ""


if ($RestartBotIfStops -eq $true) {

    while (($BotRetryDoBreak -eq $false) -and ($LASTEXITCODE -ne $OverrideRetryExitCode)) {

        $BotRetriesCountBefore = $BotCurrentRetriesCount


        try {

            python $PathMainScript

            Write-Host ""
            Write-Host ""
            Write-Host "--------------------------------------------------------------------------------------------------------->"
            Write-Host "The $PathMainScript file has stopped its execution!"
            if ($LASTEXITCODE -ne $OverrideRetryExitCode) {
                Write-Host "The Discord Bot has stopped and needs to retry!"
                Write-Host "Relaunching $PathMainScript in $BotRetrySleepSeconds seconds..."
            }
            Write-Host "<---------------------------------------------------------------------------------------------------------"

        }


        catch {

            $BotCurrentRetriesCount = $BotCurrentRetriesCount + 1

            Write-Host ""
            Write-Host "------------------------------------------->"
            Write-Host "Couldn't launch $PathMainScript."
            Write-Host ""
            Write-Host "    ERROR:"
            Write-Host "*   $_"
            Write-Host ""
            Write-Host "Retrying in $BotRetrySleepSeconds seconds.."
            Write-Host "Retry: $BotCurrentRetriesCount out of $BotMaxRetriesCount."
            Write-Host "<-------------------------------------------"
        }


        if ($BotCurrentRetriesCount -eq $BotRetriesCountBefore) { # If there was no retry (this could be replaced by 'else' in programming languages)

            $BotCurrentRetriesCount = 0 # Reset the counter if there was a successful retry.

        } elseif ($BotCurrentRetriesCount -ge $BotMaxRetriesCount) {

            Write-Host ""
            Write-Host ""
            Write-Host ""
            Write-Host "==================================================================>"
            Write-Host " ********** IMPORTANT **********"
            Write-Host " MAX AMMOUNT OF RETRIES REACHED ($BotMaxRetriesCount)"
            Write-Host ""
            Write-Host " THE SCRIPT WILL STOP EXECUTING AND NO LONGER RETRY TO SAVE POWER."
            Write-Host " ********** IMPORTANT **********"
            Write-Host "<=================================================================="

            break

        }

        if ($LASTEXITCODE -ne $OverrideRetryExitCode) {

            Start-Sleep $BotRetrySleepSeconds

            Write-Host ""
            Write-Host "----------->"
            Write-Host "Retrying..."
            Write-Host "<-----------"

        }
    }


} else {
    python $PathMainScript
}


Write-Host ""
Write-Host ""
Write-Host "--------------------------------------------------------------------------------------------------------->"
Write-Host "This script has finished it's execution Bye!"
Write-Host "The Discord Bot has stopped! The $PathMainScript file has stopped its execution!"
Write-Host "<---------------------------------------------------------------------------------------------------------"
Write-Host ""
Write-Host "Close the terminal or restart the bot if You want to..."
Write-Host ""
