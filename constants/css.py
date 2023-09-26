STYLE = """
.main {
  width: 75% !important;
  margin: auto;
}

.ninty-five-width {
  width: 95% !important;
  margin: auto;
}

.center-label > label > span {
  display: block !important;
  text-align: center;
}

.no-label {
  padding: 0px !important;
}

.no-label > label > span {
  display: none;
}

.wrap {
  min-width: 0px !important;
}

.markdown-center {
  text-align: center;
}

.markdown-left {
  text-align: left;
}

.markdown-left > div:nth-child(2) {
  padding-top: 10px !important;
}

.markdown-center > div:nth-child(2) {
  padding-top: 10px;
}

.no-gap {
  flex-wrap: initial !important;
  gap: initial !important;
}

.no-width {
  min-width: 0px !important;
}

.icon-buttons {
  display: none !important;
}

.title-width {
  display: content !important;
}

.left-margin {
  padding-left: 50px;
  background-color: transparent;
  border: none;
}

.no-border > div:nth-child(1){
  border: none;
  background: transparent;
}

textarea {
  border: none !important;
  border-radius: 0px !important;
  --block-background-fill: transparent !important;
}

#chatbot {
  height: 800px !important;
  box-shadow: 6px 5px 10px 1px rgba(255, 221, 71, 0.15);
  border-color: beige;
  border-width: 2px;  
}

#chatbot .wrapper {
  height: 660px;
}

.small-big-textarea > label > textarea {
  font-size: 12pt !important;
}

.control-button {
  background: none !important;
  border-color: #69ade2 !important;
  border-width: 2px !important;
  color: #69ade2 !important;
}

.small-big {
  font-size: 15pt !important;
}

.no-label-chatbot > div > div:nth-child(1) {
  display: none;
}

#chat-section {
  position: fixed;
  align-self: end;
  width: 65%;
  z-index: 10000;
  border: none !important;
  background: none;
  padding-left: 0px;
  padding-right: 0px;
}

#chat-section > div:nth-child(3) {
  # background: white;
}

#chat-section .form {
  position: relative !important;
  bottom: 130px;
  width: 90%;
  margin: auto;
  border-radius: 20px;
}

#chat-section .icon {
  display: none;
}

#chat-section .label-wrap {
  text-align: right;
  display: block;
}

#chat-section .label-wrap span {
  font-size: 30px;
}

#chat-buttons {
  position: relative !important;
  bottom: 130px;
  width: 90%;
  margin: auto;
}

@media only screen and (max-width: 500px) {
  .main {
    width: 100% !important;
    margin: auto;
  }
  
  #chat-section {
    width: 95%;
  }
}

.font-big textarea {
  font-size: 19pt !important;
  text-align: center;
}

.no-label-image-audio > div:nth-child(2) {
  display: none;
}

.no-label-radio > span {
  display: none;
}
"""