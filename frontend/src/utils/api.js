export function getResults(data) {
  if (Array.isArray(data)) {
    return data;
  }

  return data?.results ?? [];
}

export function getPagination(data) {
  if (!data || Array.isArray(data)) {
    return {
      count: Array.isArray(data) ? data.length : 0,
      next: null,
      previous: null,
    };
  }

  return {
    count: data.count ?? 0,
    next: data.next ?? null,
    previous: data.previous ?? null,
  };
}