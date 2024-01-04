import '../sass/project.scss';
//import "../sass/*.scss";
import { themeChange } from 'theme-change';
themeChange();

/* Project specific Javascript goes here. */
function checkStep(evt) {
  console.log(evt);
  var steps = document.getElementsByClassName('step');
  for (var i = 0; i < steps.length; i++) {
    steps[i].className.replace('step-success', 'step-primary');
  }
  evt.currentTarget.className.replace('step-primary', 'step-success');
}

function openTab(evt) {
  console.log(evt);
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
