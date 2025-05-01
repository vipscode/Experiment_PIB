document.addEventListener("DOMContentLoaded", function () {
  fetch('data/categorized_data.json')
    .then(response => response.json())
    .then(data => {
      const categories = {};

      // Group articles by category
      data.forEach(article => {
        const category = article.category || "Others";
        if (!categories[category]) {
          categories[category] = [];
        }
        categories[category].push(article);
      });

      const container = document.getElementById("categories");

      Object.keys(categories).sort().forEach(category => {
        const categoryBlock = document.createElement("div");
        categoryBlock.classList.add("category-block");

        const title = document.createElement("div");
        title.classList.add("category-title");
        title.textContent = category;
        categoryBlock.appendChild(title);

        const list = document.createElement("ul");
        list.classList.add("article-list");

        categories[category].forEach(article => {
          const item = document.createElement("li");
          item.classList.add("article-item");

          const link = document.createElement("a");
          link.href = article.link || "#";
          link.textContent = article.title;
          link.target = "_blank";

          item.appendChild(link);
          list.appendChild(item);
        });

        categoryBlock.appendChild(list);
        container.appendChild(categoryBlock);
      });
    })
    .catch(error => {
      console.error("Error loading categorized_data.json:", error);
    });
});
