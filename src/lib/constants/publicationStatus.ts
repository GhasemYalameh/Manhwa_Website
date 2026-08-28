export type PublicationStatus = "cp" | "c" | "up";

export const PUBLICATION_STATUS_LABEL: Record<PublicationStatus, string> = {
  cp: "در حال پخش",
  c: "پایان‌یافته",
  up: "منتشرنشده",
};

export const PUBLICATION_STATUS_COLOR: Record<PublicationStatus, string> = {
  cp: "bg-warning",
  c: "bg-success",
  up: "bg-error",
};
