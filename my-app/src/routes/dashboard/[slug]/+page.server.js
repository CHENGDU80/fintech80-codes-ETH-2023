import { companies } from "$lib/config/companies";
/** @type {import('./$types').PageLoad} */
export async function load({ params }) {
  let url = "http://0.0.0.0:1234/api/events";
  let ps = {
    target_entity: "electric car OR charging station OR battery technology",
    date_start: "2023-10-24",
    date_end: "2023-11-03",
    token: "K6tyfzrSrVjRHHqOaeHNI3OM7IPk82ky",
  };

  const getToday = () => {
    const today = new Date();
    const yyyy = today.getFullYear();
    const mm = String(today.getMonth() + 1).padStart(2, "0");
    const dd = String(today.getDate()).padStart(2, "0");
    return `${yyyy}-${mm}-${dd}`;
  };

  const todayDate = getToday();
  let eventsToday = [];
  let eventsOtherDays = [];

  try {
    const response = await fetch(url + "?" + new URLSearchParams(ps));

    if (!response.ok) {
      throw new Error("Network response was not ok");
    }

    const data = await response.json();

    data.event_object_jsons.forEach((/** @type {string} */ eventJsonStr) => {
      const eventObj = JSON.parse(eventJsonStr);
      if (eventObj.for_date === todayDate) {
        eventsToday.push(eventObj);
      } else {
        eventsOtherDays.push(eventObj);
      }
    });
  } catch (error) {
    console.log("There was a problem with the fetch operation:", error.message);
  }

  async function fetchCompanyData(company) {
    let url = "http://0.0.0.0:1234/api/company_data";
    let ps = {
      target_entity: company,
      token: "K6tyfzrSrVjRHHqOaeHNI3OM7IPk82ky",
    };
    try {
      const response = await await fetch(url + "?" + new URLSearchParams(ps));
      if (!response.ok) {
        throw new Error("Network response was not ok");
      }

      const data = await response.json();
      console.log(JSON.parse(data.object_json).score_combined);
      return JSON.parse(data.object_json).score_combined;
    } catch (error) {
      console.error("Error fetching data for company:", company, error);
      return null;
    }
  }
  let allCompanyData = {};
  async function fetchAllCompanies() {
    for (const company of companies.logos) {
      const data = await fetchCompanyData(company.symbol);

      allCompanyData[company.symbol] = data;
    }
    console.log(allCompanyData);
    console.log("Fetched data for all companies.");
  }
  await fetchAllCompanies();
  return {
    news: {
      daily: eventsToday,
      weekly: eventsOtherDays,
    },
    companies: {
      score: allCompanyData,
    },
  };
}
