FAQ
===

Frivoler AkaBlas-Quatsch. Oder so ähnlich.

Warum?
------

Warum nicht? Nein ernsthaft, wenn mal wieder drei Wochen am Stück neue Klarinetten dazu gekommen sind, verliert man einfach den Überblick und die nächste SoFa, auf der man vernünftig Namen lernen kann ist meist noch lange hin.
Die Idee stammt tatsächlich ursprünglich von Nora.

Warum ist das ganze ein Telegram-Bot und keine unabhängige App?
---------------------------------------------------------------

Telegram ist plattformunabhängig, d.h. Du kannst den Bot auf Deinem

* Android-Smartphone/Tablet
* Apple-Smartphone/Tablet
* anderem Smartphone/Tablet, für das es eine Telegram-App gibt
* Deinem PC/Mac über den `Telegram Desktop-Client <https://desktop.telegram.org>`_
* Lieblings-Browser über `Telegram-Web <https://web.telegram.org/k/>`_

nutzen, ohne dass Hirsch Apps für drölf verschiedene Geräte programmieren muss. Dazu hat er weder Lust, Zeit noch genug Programmierkenntnisse.

Außerdem kennt sich Hirsch mit Telegram-Bots aus und es ist relativ einfach z.B. neue Nutzer hinzuzufügen und Daten zu ändern.
Bei einer App übersteigt so etwas leider Hirschs Fähigkeiten und es müsste jedes mal ein Update geben, dass Du manuell installieren müsstest.

Einen Anlauf für eine App gab es Anfang 2019 übrigens trotzdem. Die App lief allerdings nur unter Android, war nicht sonderlich ausgefeilt und es haben sich nur wenige AkaBlasen gemeldet, die daran interessiert gewesen wären, in der App zu finden zu sein.

Warum dann Telegram und nicht WhatsApp?
---------------------------------------

Bei WhatsApp gibt es Bots nur für Firmenkunden.

Manchmal reagiert der Bot sehr langsam. Ist das normal?
-------------------------------------------------------

Wenn viele AkaBlasen gleichzeitig den Bot benutzen kann es passieren, dass er ein bisschen träge wird. Bitte hab ein bisschen Geduld mit ihm.

Warum muss ich mein Geschlecht angeben? Ist das nicht voll 2010?
----------------------------------------------------------------

    Geschlechter sind wie die World Trade Center-Türme: Früher gab es zwei davon und heute ist es ein sensibles Thema.

Der Grund ist ganz einfach: Wenn der Bot ein Bild eines vollbärtigen Mannes zeigt und Dich fragt, ob diese Person

* Anna
* Annette
* Ann-Sophie oder
* Klaus

heißt, ist auch nach 2020 die Frage nicht sonderlich schwierig. Dein Geschlecht wird als nur dafür genutzt, Fragen sinnvoll zu stellen. Wenn Du Dein Geschlecht nicht angeben möchtest, ist das okay - dann wird Dein Vorname nur nicht für andere Bot-Nutzer in den Fragen zu Verfügung stehen.
Wenn Du möchtest, dass andere AkaBlasen Deinen Vornamen lernen können, Du Dich aber nicht mit »männlich« oder »weiblich« identifizieren möchtest, kannst Du

* das Geschlecht angeben, das andere *wahrscheinlich* mit Deinem Vornamen assoziieren oder
* eine Münze werfen.

Warum bin ich als "Pärchenwart" gelistet und nicht als Männer-/Frauenwart?
-------------------------------------------------------------------------

Das Problem ist das gleiche wie beim Geschlecht: Die Fragen würden teils sehr einfach. Aber keine Angst, im Freitextmodus werden »Männerwart« und »Frauenwart« natürlich trotzdem akzeptiert!

Der Bot nimmt meine Adresse nicht an. Ist der blöd?
---------------------------------------------------

Ja. Bzw. `OpenStreetMap`_  und `Photon`_ sind blöd. Damit als Antworten für Adressen im Freitext-Modus sowohl Adressen, als auch Standorte und Koordinaten angenommen werden können,
nutzt der Bot diese beiden Dienste, um für Deine Adresse die genauen Koordinaten auszulesen. Gleichzeitig erlaubt Dir das, beim angeben einer Adresse z.B. ``Str.`` statt ``Straße`` zu schreiben.

Bei manchen Adressen ist es leider nicht ganz einfach, die Koordinaten online nach zuschlagen und der Bot erkennt Deine Adresse nicht korrekt.
Um ihm auf die Sprünge zu helfen, kannst Du

1. versuchen, statt Deiner Adresse Deinen *Standort* zu schicken. Das hilft häufig schon.
2. die Koordinaten Deines Domizils selbst herausfinden und dem Bot schicken. Bei `OpenStreetMap`_ geht das so:

  1. Gib Deine Adresse ein
  2. Wähle den passenden Treffer aus
  3. Klicke auf »Teilen«
  4. Kopiere die »Geo-URI« und schicke sie dem Bot.

.. _`OpenStreetMap`: https://www.openstreetmap.org/
.. _`Photon`: http://photon.komoot.de

Ich habe eine Fehlermeldung bekommen. Was muss ich tun?
-------------------------------------------------------

Nichts. In der Regel wird Hirsch informiert und wird eventuell bis zur nächsten Sonnenwende den Fehler behoben haben.
Falls Du den Bot tatsächlich gar nicht mehr zu *irgendetwas* bewegen kannst, kannst Du Hirsch natürlich trotzdem noch mal selber kontaktieren (Die AkaDressen sind Dein Freund).

Meine Freitext-Antwort wurde als falsch gewertet, obwohl da nur in Tippfehler drin war. Was ist da los?
-------------------------------------------------------------------------------------------------------

Tatsächlich ist es gar nicht so einfach, zu entscheiden, wann eine Freitext-Antwort noch als richtig gewertet werden kann.
Wenn die richtige Antwort ``Universitätsplatz 2, 38106 Braunschweig`` lautet, was ist dann richtig und was ist falsch?

* Universitätsplatz 2, 38106 BS
* Universitätsstraße 2, 38106 Braunschweig
* Universitätsstraße 2, Braunschweig
* Universitätsplatz 5, Braunschweig
* Unileverplatz 2, 38106 Braunschweig

Diese Entscheidung ist schon für Menschen nicht trivial - für Bots erst recht.

Der AkaNamen-Bot benutzt ein Software-Paket namens ``fuzzywuzzy``, das es möglich macht, die Ähnlichkeit von Texten zu bewerten.
Der Bot ist dabei schon ziemlich großzügig. Trotzdem wird der Bot manchmal Antworten als falsch markieren, ob wohl sie (mehr oder weniger) richtig sind - und andersherum.
Daher ist der Freitext-Modus als »für Fortgeschrittene« gekennzeichnet.

*Übrigens:* Wenn Du nach eine Adresse gefragt wirst, kannst Du als Antwort auch einen Standort senden!

Kann der Bot nicht auch noch … ?
--------------------------------

Wenn Du einen Vorschlag hast, wie der Bot verbessert oder erweitert werden kann, melde Dich gerne bei Hirsch. Es ist allerdings nicht garantiert, dass alle Vorschläge auch übernommen werden können.
