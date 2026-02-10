import '../sass/project.scss';
import * as frontEnd from '../front-end/main.jsx';
import { themeChange } from 'theme-change';

themeChange();

window.onload = function() {
	// var t = localStorage.getItem("theme");
	// document.documentElement.setAttribute("data-theme", t === "dark" ? "dark" : "light");

	const THEME_KEY = "theme";
  const checkbox = document.getElementById("theme-controller");
  if (!checkbox) return;

  function setTheme(theme) {
    document.documentElement.setAttribute("data-theme", theme);
    checkbox.checked = (theme === "dark"); // keep swap UI in sync
  }

  // 1) Load saved theme (default: light)
  const saved = localStorage.getItem(THEME_KEY);
  setTheme(saved === "dark" ? "dark" : "light");

  // 2) Save + apply when toggled
  checkbox.addEventListener("change", () => {
    const theme = checkbox.checked ? "dark" : "light";
    setTheme(theme);
    localStorage.setItem(THEME_KEY, theme);
  });
}

function checkStep(evt) {
  var steps = document.getElementsByClassName('step');
  for (var i = 0; i < steps.length; i++) {
    steps[i].className.replace('step-success', 'step-primary');
  }
  evt.currentTarget.className.replace('step-primary', 'step-success');
}

function openTab(evt) {
  var tablinks = document.getElementsByClassName('tablink');
  for (var i = 0; i < tablinks.length; i++) {
    tablinks[i].className = tablinks[i].className.replace(
      ' text-icon-green bg-gray-200 mr-[-2px]',
      '',
    );
  }
  evt.currentTarget.className += ' text-icon-green bg-gray-200 mr-[-2px]';
}

var x = document.getElementById('defaultOpen');
if (x != null) {
  x.click();
}
