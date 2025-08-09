const getBackendBaseUrl = () => {
  const apiUrl =
    import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api/v1";
  try {
    const url = new URL(apiUrl);
    return url.origin + "/media";
  } catch (e) {
    return "http://localhost:8000/media";
  }
};

export const getFullUrl = (path) => {
  if (!path) {
    return "";
  }
  if (path.startsWith("http://") || path.startsWith("https://")) {
    return path;
  }
  const baseUrl = getBackendBaseUrl();
  return `${baseUrl}${path.startsWith("/") ? "" : "/"}${path}`;
};
