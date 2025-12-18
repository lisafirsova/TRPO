const themeToggle = document.getElementById("theme-toggle");
const settingsIcon = document.getElementById("settings-icon");
const body = document.body;
const darkThemeKey = 'isDarkMode'; 


function applyTheme(isDark) {
    if (isDark) {
        body.classList.add('dark-mode');
        if (settingsIcon) {
            settingsIcon.classList.add('rotated');
        }
    } else {
        body.classList.remove('dark-mode');
        if (settingsIcon) {
            settingsIcon.classList.remove('rotated');
        }
    }
    localStorage.setItem(darkThemeKey, isDark);
}

const isDarkModeStored = localStorage.getItem(darkThemeKey) === 'true';
applyTheme(isDarkModeStored);

if (themeToggle) {
    themeToggle.addEventListener('click', (event) => {
        event.preventDefault(); 
        const newIsDarkMode = !body.classList.contains('dark-mode');
        applyTheme(newIsDarkMode);
    });
}