@echo off
cd /d "%~dp0"
title yusuke-trap - Gerador de videos

echo ==================================================
echo   yusuke-trap  -  imagem + audio  =^>  MP4 (Ken Burns)
echo ==================================================
echo.
echo   Pareia arquivos de mesmo nome:
echo     input\image\NOME.(jpg/png/webp...)
echo     input\audio\NOME.(mp3/wav/flac...)
echo   Gera: output\NOME.mp4
echo.
echo   Regras:
echo     - [render] gera o video do par
echo     - [skip]   ja existe em output, nao refaz (idempotencia)
echo     - [warn]   arquivo sem par e ignorado
echo.
echo   Dica: para REFAZER os videos existentes, rode:  run.bat --force
echo ==================================================
echo.

if not exist ".venv\Scripts\python.exe" (
    echo [ERRO] Ambiente virtual nao encontrado em .venv
    echo.
    echo   Crie e instale as dependencias com:
    echo     python -m venv .venv
    echo     .venv\Scripts\python.exe -m pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)

".venv\Scripts\python.exe" -m src.main %*
set "EXITCODE=%ERRORLEVEL%"

echo.
echo ==================================================
if "%EXITCODE%"=="0" (
    echo   Processamento finalizado SEM falhas.
) else (
    echo   Processamento finalizado COM falhas. Veja [fail] acima.
)
echo   Videos em: output\
echo ==================================================
echo.
pause
