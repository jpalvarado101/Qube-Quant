import { Injectable } from "@angular/core";

@Injectable({ providedIn: "root" })
export class ApiService {
  base = "/api";
  async syncPrices(symbol: string, start: string, end: string) {
    const res = await fetch(
      `${this.base}/data/sync/prices?symbol=${symbol}&start=${start}&end=${end}`,
      { method: "POST" }
    );
    return res.json();
  }
  async train(body: any) {
    const res = await fetch(`${this.base}/runs/train`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    return res.json();
  }
}
