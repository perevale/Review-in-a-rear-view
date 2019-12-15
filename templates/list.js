const COLORS = [
  '#FE9',
  '#9AF',
  '#F9A',
  "#AFA",
  "#FA7"
];

function addItem(container, template) {
  let color = COLORS[_.random(COLORS.length - 1)];
  let num = _.random(10000);

  container.append(Mustache.render(template, { color, num }));
}

$(() => {
  const tmpl = $('#item_template').html()
  const container = $('#app');

  for(let i=0; i<5; i++) { addItem(container, tmpl); }

  $('#add_el').click(() => {
    addItem(container, tmpl);
  })

  container.on('click', '.del_el', (e) => {
    $(e.target).closest('.item').remove();
  });
});