call ./venv/Scripts/activate

:: Change to the directory where the .spec files are located
cd spec

:: Loop through each .spec file and run PyInstaller
for %%f in (*.spec) do (
    call python -m PyInstaller --noconfirm --distpath "E:\ProjectLexeme\dist" --workpath "E:\ProjectLexeme\build" "%%f"
)
echo Finished compiling all language files
pause