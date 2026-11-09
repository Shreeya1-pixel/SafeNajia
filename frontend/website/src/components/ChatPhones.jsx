/**
 * NABD-style phone mockups for WhatsApp + Instagram visual demos.
 */
import { useEffect, useRef } from "react";

function clock() {
  return new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", hour12: false });
}

export function WhatsAppPhone({ messages, contact = "GTBank Support", typing = false }) {
  const endRef = useRef(null);
  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, typing]);

  return (
    <div className="ng-phone wa">
      <div className="ng-phone-bezel">
        <div className="ng-phone-notch" />
        <div className="ng-phone-status wa">
          <span>{clock()}</span>
          <span>5G ▮▮▮</span>
        </div>
        <div className="ng-phone-header wa">
          <span className="ng-back">‹</span>
          <span className="ng-avatar wa">GB</span>
          <div className="ng-contact">
            <strong>{contact} ✓</strong>
            <em>{typing ? "typing…" : "online"}</em>
          </div>
          <span className="ng-icons">📹 📞 ⋮</span>
        </div>
        <div className="ng-phone-thread wa">
          <div className="ng-day">Today</div>
          <div className="ng-official">Messages are end-to-end encrypted. Demo chat — not a real bank.</div>
          {messages.map((m) => (
            <div key={m.id} className={`ng-bubble ${m.side} ${m.decision ? m.decision.toLowerCase() : ""}`}>
              {m.side === "bot" && m.decision && (
                <div className="ng-bubble-tag">SafeNaija · {m.decision}</div>
              )}
              {m.side === "in" && m.lang && (
                <div className="ng-bubble-lang">{m.lang}</div>
              )}
              <p>{m.text}</p>
              <span className="ng-time">
                {m.time || clock()}
                {m.side === "out" ? " ✓✓" : ""}
              </span>
            </div>
          ))}
          {typing && (
            <div className="ng-bubble in typing">
              <span /><span /><span />
            </div>
          )}
          <div ref={endRef} />
        </div>
        <div className="ng-phone-composer wa">
          <div className="ng-composer-input">Message</div>
          <div className="ng-mic">🎤</div>
        </div>
      </div>
      <p className="ng-phone-caption">WhatsApp · visual demo</p>
    </div>
  );
}

export function InstagramPhone({ messages, contact = "naija_crypto_vip", typing = false }) {
  const endRef = useRef(null);
  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, typing]);

  return (
    <div className="ng-phone ig">
      <div className="ng-phone-bezel ig">
        <div className="ng-phone-notch" />
        <div className="ng-phone-status ig">
          <span>{clock()}</span>
          <span>5G ▮▮▮</span>
        </div>
        <div className="ng-phone-header ig">
          <span className="ng-back dark">‹</span>
          <span className="ng-avatar ig">{contact.slice(0, 1).toUpperCase()}</span>
          <div className="ng-contact dark">
            <strong>{contact}</strong>
            <em>{typing ? "Active now" : "Instagram · Direct"}</em>
          </div>
          <span className="ng-icons dark">📞 ⓘ</span>
        </div>
        <div className="ng-phone-thread ig">
          <div className="ng-ig-profile">
            <div className="ng-ig-ring">{contact.slice(0, 1).toUpperCase()}</div>
            <strong>{contact}</strong>
            <span>1.2K followers · Lagos</span>
          </div>
          {messages.map((m) => (
            <div key={m.id} className={`ng-bubble ig ${m.side} ${m.decision ? m.decision.toLowerCase() : ""}`}>
              {m.side === "bot" && m.decision && (
                <div className="ng-bubble-tag">SafeNaija · {m.decision}</div>
              )}
              <p>{m.text}</p>
              <span className="ng-time">{m.time || clock()}</span>
            </div>
          ))}
          {typing && (
            <div className="ng-bubble ig in typing">
              <span /><span /><span />
            </div>
          )}
          <div ref={endRef} />
        </div>
        <div className="ng-phone-composer ig">
          <div className="ng-composer-input ig">Message…</div>
        </div>
      </div>
      <p className="ng-phone-caption">Instagram DM · visual demo</p>
    </div>
  );
}
