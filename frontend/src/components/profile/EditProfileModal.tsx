"use client";

import { useState } from "react";
import { Modal } from "@/components/ui/Modal";
import { updateProfile, type UserProfile } from "@/lib/api/auth";
import { useToast } from "@/components/ui/Toast";
import { getCoverUrl } from "@/lib/api/manhwa";

interface EditProfileModalProps {
  profile: UserProfile;
  onClose: () => void;
  onUpdated: (profile: UserProfile) => void;
}

export function EditProfileModal({ profile, onClose, onUpdated }: EditProfileModalProps) {
  const { showToast } = useToast();
  const [firstName, setFirstName] = useState(profile.first_name);
  const [lastName, setLastName] = useState(profile.last_name);
  const [avatarFile, setAvatarFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(
    profile.avatar ? getCoverUrl(profile.avatar) : null
  );
  const [isSaving, setIsSaving] = useState(false);

  function handleFileChange(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    setAvatarFile(file);
    setPreviewUrl(URL.createObjectURL(file));
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!firstName.trim() || isSaving) return;
    setIsSaving(true);
    try {
      const updated = await updateProfile({
        first_name: firstName.trim(),
        last_name: lastName.trim(),
        ...(avatarFile ? { avatar: avatarFile } : {}),
      });
      // پچ فقط سه فیلد رو برمی‌گردونه؛ با بقیه‌ی پروفایل (phone_number, is_subscriber) merge می‌کنیم
      onUpdated({ ...profile, ...updated });
      showToast("اطلاعات با موفقیت به‌روزرسانی شد.", "success");
      onClose();
    } catch {
      showToast("به‌روزرسانی اطلاعات با خطا مواجه شد.", "error");
    } finally {
      setIsSaving(false);
    }
  }

  return (
    <Modal title="ویرایش اطلاعات" onClose={onClose}>
      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        <div className="flex flex-col items-center gap-2">
          <div className="h-20 w-20 overflow-hidden rounded-full bg-accent-light">
            {previewUrl ? (
              // eslint-disable-next-line @next/next/no-img-element
              <img src={previewUrl} alt="" className="h-full w-full object-cover" />
            ) : (
              <span className="flex h-full w-full items-center justify-center text-xl font-semibold text-accent">
                {firstName.charAt(0) || "?"}
              </span>
            )}
          </div>
          <label className="cursor-pointer text-xs text-accent hover:underline">
            تغییر عکس پروفایل
            <input type="file" accept="image/*" onChange={handleFileChange} className="hidden" />
          </label>
        </div>

        <div className="flex flex-col gap-1">
          <label className="text-xs text-text-secondary">نام</label>
          <input
            type="text"
            value={firstName}
            onChange={(e) => setFirstName(e.target.value)}
            dir="auto"
            className="rounded-card border border-divider bg-bg px-3 py-2 text-sm text-text-primary outline-none focus:border-accent"
          />
        </div>

        <div className="flex flex-col gap-1">
          <label className="text-xs text-text-secondary">نام‌خانوادگی</label>
          <input
            type="text"
            value={lastName}
            onChange={(e) => setLastName(e.target.value)}
            dir="auto"
            className="rounded-card border border-divider bg-bg px-3 py-2 text-sm text-text-primary outline-none focus:border-accent"
          />
        </div>

        <button
          type="submit"
          disabled={!firstName.trim() || isSaving}
          className="mt-2 rounded-card bg-accent px-4 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-accent-dark disabled:opacity-50"
        >
          {isSaving ? "در حال ذخیره..." : "ذخیره تغییرات"}
        </button>
      </form>
    </Modal>
  );
}
