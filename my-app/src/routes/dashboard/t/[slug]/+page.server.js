import { error } from "@sveltejs/kit";
/** @type {import('./$types').PageLoad} */ export async function load({
  params,
}) {
  let slug = params.slug;
  let url = "http://0.0.0.0:1234/api/lst_news_by_event_id";
  let ps = {
    event_id: slug,
    token: "K6tyfzrSrVjRHHqOaeHNI3OM7IPk82ky",
  };

  let objs = [];
  try {
    const response = await fetch(url + "?" + new URLSearchParams(ps));

    if (!response.ok) {
      throw new Error("Network response was not ok");
    }

    const data = await response.json();
    console.log(data);
    objs = data.object_json.map((/** @type {string} */ item) => {
      return JSON.parse(item);
    });
    console.log(objs);
  } catch (error) {
    console.log("There was a problem with the fetch operation:", error.message);
  }

  return {
    objs: objs,
  };
}
