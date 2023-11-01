/** @type {import('./$types').PageLoad} */
export async function load({ params }) {
  let url = "http://0.0.0.0:1234/api/events";
  let slug = params.slug;
  let ps = {
    target_entity: slug,
    date_start: "2023-10-24",
    date_end: "2023-11-03",
    token: "K6tyfzrSrVjRHHqOaeHNI3OM7IPk82ky",
  };
  let objs = [];
  try {
    const response = await fetch(url + "?" + new URLSearchParams(ps));

    if (!response.ok) {
      throw new Error("Network response was not ok");
    }

    const data = await response.json();
    objs = data.event_object_jsons.map((item) => {
      return JSON.parse(item);
    });
    console.log(objs);
  } catch (error) {
    console.log("There was a problem with the fetch operation:", error.message);
  }

  return {
    news: objs,
    company: slug,
  };
}
