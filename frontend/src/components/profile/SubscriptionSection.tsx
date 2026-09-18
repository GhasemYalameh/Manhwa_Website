"use client";

import { useEffect, useState } from "react";
import { useToast } from "@/components/ui/Toast";
import {
  getSubscriptionStatus,
  getSubscriptionPlans,
  getSubscriptionOrders,
  purchaseSubscription,
  type SubscriptionStatus,
  type SubscriptionPlan,
  type SubscriptionOrder,
} from "@/lib/api/subscription";

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString("fa-IR");
}

export function SubscriptionSection() {
  const { showToast } = useToast();
  const [status, setStatus] = useState<SubscriptionStatus | null>(null);
  const [plans, setPlans] = useState<SubscriptionPlan[]>([]);
  const [orders, setOrders] = useState<SubscriptionOrder[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [purchasingPlanId, setPurchasingPlanId] = useState<number | null>(null);

  useEffect(() => {
    Promise.all([getSubscriptionStatus(), getSubscriptionPlans(), getSubscriptionOrders()])
      .then(([statusRes, plansRes, ordersRes]) => {
        setStatus(statusRes);
        setPlans(plansRes);
        setOrders(ordersRes);
      })
      .catch(() => {
        showToast("خطا در دریافت اطلاعات اشتراک.", "error");
      })
      .finally(() => setIsLoading(false));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function handlePurchase(planId: number) {
    if (purchasingPlanId !== null) return;
    setPurchasingPlanId(planId);
    try {
      const res = await purchaseSubscription(planId);
      window.location.href = res.payment_url;
    } catch {
      showToast("ایجاد درخواست پرداخت با خطا مواجه شد.", "error");
      setPurchasingPlanId(null);
    }
  }

  if (isLoading) {
    return (
      <section className="mx-auto max-w-[1400px] px-4 py-8 lg:px-8">
        <p className="text-sm text-text-secondary">در حال بارگذاری اطلاعات اشتراک...</p>
      </section>
    );
  }

  return (
    <section className="mx-auto max-w-[1400px] px-4 py-8 lg:px-8">
      <h2 className="mb-4 text-lg font-bold text-text-primary">اشتراک</h2>

      {/* وضعیت فعلی */}
      <div className="rounded-card bg-surface p-5">
        {status?.is_subscriber ? (
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div>
              <p className="text-sm font-semibold text-success">اشتراک شما فعال است</p>
              <p className="mt-1 text-xs text-text-secondary">
                تاریخ انقضا: {formatDate(status.expiration_date)}
              </p>
            </div>
            <span className="rounded-full bg-success/15 px-3 py-1 text-xs font-semibold text-success">
              فعال
            </span>
          </div>
        ) : (
          <div className="flex flex-wrap items-center justify-between gap-3">
            <p className="text-sm text-text-secondary">شما در حال حاضر اشتراک فعالی ندارید.</p>
            <span className="rounded-full bg-error/15 px-3 py-1 text-xs font-semibold text-error">
              غیرفعال
            </span>
          </div>
        )}
      </div>

      {/* پلن‌ها */}
      <div className="mt-6 grid grid-cols-[repeat(auto-fill,minmax(220px,1fr))] gap-4">
        {plans.map((plan) => (
          <div key={plan.id} className="flex flex-col gap-3 rounded-card bg-surface p-5">
            <span className="text-sm font-bold text-text-primary">{plan.name}</span>
            <span className="text-xs text-text-secondary">
              {plan.duration.toLocaleString("fa-IR")} روز
            </span>
            <span className="text-lg font-extrabold text-accent">
              {plan.price.toLocaleString("fa-IR")} تومان
            </span>
            <button
              type="button"
              disabled={purchasingPlanId !== null}
              onClick={() => handlePurchase(plan.id)}
              className="mt-2 rounded-card bg-accent px-4 py-2 text-sm font-semibold text-white transition-colors hover:bg-accent-dark disabled:opacity-50"
            >
              {purchasingPlanId === plan.id ? "در حال انتقال..." : "خرید این پلن"}
            </button>
          </div>
        ))}
      </div>

      {/* تاریخچه سفارش‌ها */}
      {orders.length > 0 && (
        <div className="mt-8">
          <h3 className="mb-3 text-sm font-bold text-text-primary">تاریخچه‌ی خرید</h3>
          <div className="flex flex-col divide-y divide-divider overflow-hidden rounded-card bg-surface">
            {orders.map((order, index) => (
              <div key={index} className="flex flex-wrap items-center justify-between gap-2 px-4 py-3 text-sm">
                <span className="text-text-primary">{order.plan.name}</span>
                <span className="text-text-secondary">{formatDate(order.created_at)}</span>
                <span
                  className={`rounded-full px-2.5 py-0.5 text-[11px] font-semibold ${
                    order.is_paid ? "bg-success/15 text-success" : "bg-error/15 text-error"
                  }`}
                >
                  {order.is_paid ? "پرداخت‌شده" : "پرداخت‌نشده"}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </section>
  );
}
