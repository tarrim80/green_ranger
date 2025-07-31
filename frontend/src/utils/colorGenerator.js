export function generateUniqueRandomColor(existingColors = []) {
  const existingSet = new Set(existingColors.map((c) => c.toUpperCase()));
  let randomColor;

  do {
    randomColor =
      "#" +
      Math.floor(Math.random() * 16777215)
        .toString(16)
        .padStart(6, "0")
        .toUpperCase();
  } while (existingSet.has(randomColor));

  return randomColor;
}
