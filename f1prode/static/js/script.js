let position = 1;
let inputs;
let input;
let card;
const activateCard = (id, cardId, inputId, divId) => {
  document.getElementById(cardId).onclick = () => {
    card = document.getElementById(cardId);
    input = document.getElementById(inputId);
    div = document.getElementById(divId);
    if (!input.hasAttribute("hasbeenset")) {
      input.setAttribute("value", position);
      input.setAttribute("hasbeenset", true);
      div.append(position);
      div.style.display = "block";
      position++;
      paintIt(id, card);
    } else if (
      input.hasAttribute("hasbeenset") &&
      Number(input.getAttribute("value")) === position - 1
    ) {
      input.removeAttribute("value");
      input.removeAttribute("hasbeenset");
      div.innerHTML = "";
      div.style.display = "none";
      position--;
      paintIt(id, card);
    }
  };
};
const paintIt = (id, it) => {
  if (id % 2 == 1) {
    if (it.style.background == "black") {
      it.style.background = "whitesmoke";
      it.style.color = "black";
    } else {
      it.style.background = "black";
      it.style.color = "whitesmoke";
    }
  }
};
const animateCars = () => {
  const cars = document.querySelectorAll(".car");
  let i = 1;
  cars.forEach(car => {
    console.log(`racingUp${i}`);
    car.classList.add(`racingUp${i}`);
    i++;
  });
};
const validateForm = () => {
  let inputList = document.querySelectorAll(".theInput");
  let values = [];
  for (let i = 0; i < inputList.length; i++) {
    let value = inputList[i].value;
    if (!value || isNaN(value) || value < 1 || value > 20) {
      alert("All inputs must have a value between 1 and 20.");
      return false;
    }
    if (values.includes(value)) {
      alert("Duplicate values are not allowed.");
      return false;
    }
    values.push(value);
  }
  return true;
};
document.addEventListener("DOMContentLoaded", function () {
  const form = document.querySelector("form");
  form.addEventListener("submit", function (event) {
    event.preventDefault();
    if (validateForm()) {
      animateCars();
    }
  });
});
